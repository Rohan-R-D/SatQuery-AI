import cv2
import numpy as np
from typing import Tuple, Dict, Any


class CoregistrationQualityGate:
    """
    Sub-pixel co-registration engine using SIFT/ORB feature matching,
    RANSAC homography estimation, and quantitative RMSE/NMI quality gating.
    Enforces RMSE <= 0.8px threshold to prevent false-alarm change detections.
    """
    def __init__(self, rmse_threshold: float = 0.8, nmi_threshold: float = 0.45):
        self.rmse_threshold = rmse_threshold
        self.nmi_threshold = nmi_threshold

    def compute_nmi(self, img_a: np.ndarray, img_b: np.ndarray, bins: int = 64) -> float:
        """Calculate Normalized Mutual Information between two raster arrays."""
        if img_a.ndim == 3:
            img_a = cv2.cvtColor(img_a, cv2.COLOR_RGB2GRAY)
        if img_b.ndim == 3:
            img_b = cv2.cvtColor(img_b, cv2.COLOR_RGB2GRAY)

        hist_2d, _, _ = np.histogram2d(img_a.ravel(), img_b.ravel(), bins=bins)
        p_ab = hist_2d / float(np.sum(hist_2d))
        p_a = np.sum(p_ab, axis=1)
        p_b = np.sum(p_ab, axis=0)

        # Avoid log(0)
        p_ab_nz = p_ab[p_ab > 0]
        p_a_nz = p_a[p_a > 0]
        p_b_nz = p_b[p_b > 0]

        h_a = -np.sum(p_a_nz * np.log2(p_a_nz))
        h_b = -np.sum(p_b_nz * np.log2(p_b_nz))
        h_ab = -np.sum(p_ab_nz * np.log2(p_ab_nz))

        if h_ab <= 1e-12:
            return 0.0
        return float((h_a + h_b) / h_ab)

    def align_and_validate(
        self,
        ref_img: np.ndarray,
        target_img: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Align target_img to ref_img using feature matching and homography warping.
        Returns (aligned_target_img, quality_report).
        """
        h, w = ref_img.shape[:2]
        h_t, w_t = target_img.shape[:2]

        # Convert to grayscale for keypoint detection
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY) if ref_img.ndim == 3 else ref_img
        tgt_gray = cv2.cvtColor(target_img, cv2.COLOR_RGB2GRAY) if target_img.ndim == 3 else target_img

        # 1. Feature Detection with SIFT (fallback to ORB if SIFT produces insufficient points)
        detector = cv2.SIFT_create(nfeatures=5000)
        kp1, des1 = detector.detectAndCompute(ref_gray, None)
        kp2, des2 = detector.detectAndCompute(tgt_gray, None)

        if des1 is None or des2 is None or len(kp1) < 8 or len(kp2) < 8:
            detector_orb = cv2.ORB_create(nfeatures=5000)
            kp1, des1 = detector_orb.detectAndCompute(ref_gray, None)
            kp2, des2 = detector_orb.detectAndCompute(tgt_gray, None)

        if des1 is None or des2 is None or len(kp1) < 6 or len(kp2) < 6:
            # Insufficient keypoints: resize to match shape and return warning
            resized_tgt = cv2.resize(target_img, (w, h), interpolation=cv2.INTER_LANCZOS4)
            nmi_val = self.compute_nmi(ref_img, resized_tgt)
            return resized_tgt, {
                "passed": False,
                "rmse": 999.0,
                "nmi": round(nmi_val, 3),
                "inlier_count": 0,
                "reason": "Insufficient keypoints detected for sub-pixel homography alignment."
            }

        # 2. Keypoint Matching via KNN + Lowe's Ratio Test (0.75)
        matcher = cv2.BFMatcher(cv2.NORM_L2 if des1.dtype == np.float32 else cv2.NORM_HAMMING)
        raw_matches = matcher.knnMatch(des1, des2, k=2)

        good_matches = []
        for match_pair in raw_matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

        if len(good_matches) < 6:
            resized_tgt = cv2.resize(target_img, (w, h), interpolation=cv2.INTER_LANCZOS4)
            nmi_val = self.compute_nmi(ref_img, resized_tgt)
            return resized_tgt, {
                "passed": False,
                "rmse": 999.0,
                "nmi": round(nmi_val, 3),
                "inlier_count": len(good_matches),
                "reason": f"Only {len(good_matches)} inliers found; minimum 6 required for RANSAC."
            }

        pts_ref = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        pts_tgt = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 3. Homography Estimation with RANSAC
        H, inliers = cv2.findHomography(pts_tgt, pts_ref, cv2.RANSAC, 2.5)

        if H is None or inliers is None or np.sum(inliers) < 4:
            resized_tgt = cv2.resize(target_img, (w, h), interpolation=cv2.INTER_LANCZOS4)
            nmi_val = self.compute_nmi(ref_img, resized_tgt)
            return resized_tgt, {
                "passed": False,
                "rmse": 999.0,
                "nmi": round(nmi_val, 3),
                "inlier_count": int(np.sum(inliers)) if inliers is not None else 0,
                "reason": "RANSAC failed to fit consistent homography transformation."
            }

        # 4. Compute Sub-Pixel Inlier RMSE
        inlier_mask = inliers.ravel() == 1
        inlier_tgt = np.float32(pts_tgt[inlier_mask]).reshape(-1, 1, 2)
        inlier_ref = np.float32(pts_ref[inlier_mask]).reshape(-1, 1, 2)

        transformed_tgt = cv2.perspectiveTransform(inlier_tgt, H)
        residuals = np.linalg.norm(inlier_ref - transformed_tgt, axis=2)
        rmse = float(np.sqrt(np.mean(residuals ** 2)))

        # 5. Apply Perspective Warp
        aligned_tgt = cv2.warpPerspective(target_img, H, (w, h), flags=cv2.INTER_LANCZOS4)

        # 6. Compute Normalized Mutual Information
        nmi = self.compute_nmi(ref_img, aligned_tgt)

        passed = bool(rmse <= self.rmse_threshold and nmi >= self.nmi_threshold)
        inlier_count = int(np.sum(inliers))

        return aligned_tgt, {
            "passed": passed,
            "rmse": round(rmse, 3),
            "nmi": round(nmi, 3),
            "inlier_count": inlier_count,
            "reason": "Co-registration Quality Gate PASSED (RMSE <= 0.8px)." if passed else (
                f"Co-registration Warning: RMSE ({rmse:.2f}px) exceeded 0.8px tolerance or NMI ({nmi:.2f}) < 0.45."
            )
        }


coregistration_gate = CoregistrationQualityGate()
