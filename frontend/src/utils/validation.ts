import { InputType, ImageFileMetadata } from '../types/analysis';

export interface ValidationResult {
  isValid: boolean;
  errorMessage: string | null;
}

export const validateAnalysisInput = (
  inputType: InputType,
  image1: ImageFileMetadata | null,
  image2: ImageFileMetadata | null,
  query: string
): ValidationResult => {
  // Check image requirements based on mode
  if (inputType === 'single') {
    if (!image1) {
      return { isValid: false, errorMessage: 'No image selected.' };
    }
  } else if (inputType === 'bitemporal') {
    if (!image1 || !image2) {
      return { isValid: false, errorMessage: 'Two images are required for bi-temporal analysis.' };
    }
  } else if (inputType === 'optical-sar') {
    if (!image1 || !image2) {
      return { isValid: false, errorMessage: 'Optical and SAR images are required.' };
    }
  }

  // Check query requirement
  if (!query || query.trim().length === 0) {
    return { isValid: false, errorMessage: 'Please enter a query.' };
  }

  return { isValid: true, errorMessage: null };
};
