import io
import base64
import logging
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger("satquery.change_detection")

class ChangeDetectionEngine:
    @staticmethod
    def _to_base64_data_url(cv_img: np.ndarray) -> str:
        """Helper to convert OpenCV image array (BGR or Grayscale) into base64 PNG data URL."""
        success, buffer = cv2.imencode(".png", cv_img)
        if not success:
            return ""
        b64_str = base64.b64encode(buffer).decode("utf-8")
        return f"data:image/png;base64,{b64_str}"

    def detect_changes(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        threshold_val: int = 35,
        min_region_area: int = 50
    ) -> dict:
        """
        Processes two bi-temporal satellite images (T1 Before and T2 After) using OpenCV pixel-difference thresholding.
        Returns a dictionary containing:
        - change_percentage (float)
        - changed_pixels (int)
        - total_pixels (int)
        - regions (list of dicts with x, y, width, height, area)
        - difference_map (base64 PNG)
        - change_mask (base64 PNG)
        - change_overlay (base64 PNG)
        - disclaimer (str)
        """
        try:
            # 1. Load both images from bytes
            pil_t1 = Image.open(io.BytesIO(before_bytes)).convert("RGB")
            pil_t2 = Image.open(io.BytesIO(after_bytes)).convert("RGB")

            img1_bgr = cv2.cvtColor(np.array(pil_t1), cv2.COLOR_RGB2BGR)
            img2_bgr = cv2.cvtColor(np.array(pil_t2), cv2.COLOR_RGB2BGR)

            # 2. Verify dimensions & resize img2 if needed to match img1
            h1, w1 = img1_bgr.shape[:2]
            h2, w2 = img2_bgr.shape[:2]

            if (h1, w1) != (h2, w2):
                logger.info(f"Resizing T2 image from {w2}x{h2} to match T1 {w1}x{h1}")
                img2_bgr = cv2.resize(img2_bgr, (w1, h1), interpolation=cv2.INTER_LINEAR)

            # 3. Convert to Grayscale
            gray1 = cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_bgr, cv2.COLOR_BGR2GRAY)

            # 4. Compute Absolute Difference
            diff = cv2.absdiff(gray1, gray2)

            # 5. Apply Thresholding
            _, binary_thresh = cv2.threshold(diff, threshold_val, 255, cv2.THRESH_BINARY)

            # 6. Apply Morphological Operations (Opening & Closing to remove noise)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            morphed = cv2.morphologyEx(binary_thresh, cv2.MORPH_OPEN, kernel)
            morphed = cv2.morphologyEx(morphed, cv2.MORPH_CLOSE, kernel)

            # 7. Connected Component / Contour Analysis for Region Bounding Boxes
            contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            clean_mask = np.zeros_like(morphed)
            regions = []

            for cnt in contours:
                area = int(cv2.contourArea(cnt))
                if area >= min_region_area:
                    cv2.drawContours(clean_mask, [cnt], -1, 255, thickness=cv2.FILLED)
                    x, y, w, h = cv2.boundingRect(cnt)
                    regions.append({
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": area
                    })

            # Sort regions by area descending (largest changed regions first)
            regions.sort(key=lambda r: r["area"], reverse=True)

            # 8. Calculate Metrics
            changed_pixels = int(np.sum(clean_mask > 0))
            total_pixels = int(w1 * h1)
            change_percentage = round((changed_pixels / total_pixels) * 100, 2)

            # 9. Generate Visual Overlay (Highlight changes in red on T2 image)
            overlay_bgr = img2_bgr.copy()
            red_mask = np.zeros_like(img2_bgr)
            red_mask[clean_mask > 0] = [0, 0, 255] # Red in BGR

            # Blend red highlight with original T2 image
            cv2.addWeighted(red_mask, 0.45, overlay_bgr, 1.0, 0, overlay_bgr)
            # Draw contour outlines around changed regions
            cv2.drawContours(overlay_bgr, contours, -1, (0, 255, 255), 1) # Yellow border

            # 10. Encode Visual Artifacts to Base64 Data URLs
            diff_map_url = self._to_base64_data_url(diff)
            change_mask_url = self._to_base64_data_url(clean_mask)
            overlay_url = self._to_base64_data_url(overlay_bgr)

            disclaimer = (
                "Scientific Disclaimer: This analysis uses an OpenCV pixel-difference thresholding prototype engine. "
                "It serves as a baseline spatial change pipeline and is designed to be replaced by deep-learning or CDVQA models in future releases."
            )

            return {
                "change_percentage": change_percentage,
                "changed_pixels": changed_pixels,
                "total_pixels": total_pixels,
                "regions": regions[:15], # Return top 15 significant connected regions
                "difference_map": diff_map_url,
                "change_mask": change_mask_url,
                "change_overlay": overlay_url,
                "disclaimer": disclaimer
            }

        except Exception as e:
            logger.error(f"Error executing change detection pipeline: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to process bi-temporal change detection: {str(e)}")

change_detection_engine = ChangeDetectionEngine()
