import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { FileText, Loader2, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

const SubmitFindingsModal = ({ open, onClose, investigation, onSubmit }) => {
  const [formData, setFormData] = useState({
    observations: '',
    conclusion: '',
    outcome: '',
    recommendation: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  const validateForm = () => {
    if (!formData.observations || !formData.observations.trim()) {
      setError('Observations are required');
      return false;
    }
    if (!formData.conclusion || !formData.conclusion.trim()) {
      setError('Conclusion is required');
      return false;
    }
    if (!formData.outcome) {
      setError('Outcome is required');
      return false;
    }
    if (!formData.recommendation) {
      setError('Recommendation is required');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    // Clear previous errors
    setError('');
    
    // Frontend validation
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      // Reset form on success
      setFormData({
        observations: '',
        conclusion: '',
        outcome: '',
        recommendation: '',
      });
      toast.success('Findings submitted successfully');
      onClose();
    } catch (error) {
      console.error('Submit findings error:', error);
      
      // Extract meaningful error message from API response
      let errorMessage = 'Failed to submit findings';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      observations: '',
      conclusion: '',
      outcome: '',
      recommendation: '',
    });
    setError('');
    onClose();
  };

  const isFormComplete = formData.observations && formData.conclusion && formData.outcome && formData.recommendation;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-heading">Submit Investigation Findings</DialogTitle>
          <DialogDescription className="text-sm text-slate-500">
            Complete the investigation report for{' '}
            <span className="font-medium text-slate-700">{investigation?.investigation_id}</span>
          </DialogDescription>
        </DialogHeader>

        {/* Scrollable Body */}
        <div className="px-8 py-6 space-y-6 overflow-y-auto max-h-[55vh] custom-scrollbar">
          {/* Error Alert */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border-2 border-red-200 rounded-xl">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-900">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Investigation Summary Card */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-semibold text-blue-900 mb-2">Investigation Summary</h3>
                <div className="space-y-1 text-sm">
                  <p className="text-blue-700">
                    <span className="font-medium">Claim:</span> {investigation?.claim_number}
                  </p>
                  <p className="text-blue-700">
                    <span className="font-medium">Insured:</span> {investigation?.insured_name}
                  </p>
                  <p className="text-blue-700">
                    <span className="font-medium">Category:</span> {investigation?.category_name}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Form Fields */}
          <div className="space-y-5">
            {/* Observations - Mandatory */}
            <div>
              <Label htmlFor="observations" className="text-sm font-semibold text-slate-700 mb-2 block">
                Observations <span className="text-red-500">*</span>
              </Label>
              <p className="text-xs text-slate-500 mb-2">
                Document your observations collected during the investigation
              </p>
              <Textarea
                id="observations"
                value={formData.observations}
                onChange={(e) => updateField('observations', e.target.value)}
                rows={5}
                placeholder="Detail your observations from the investigation process..."
                data-testid="findings-observations-input"
                className={error.includes('Observations') ? 'ring-2 ring-red-500' : ''}
              />
            </div>

            {/* Conclusion - Mandatory */}
            <div>
              <Label htmlFor="conclusion" className="text-sm font-semibold text-slate-700 mb-2 block">
                Conclusion <span className="text-red-500">*</span>
              </Label>
              <p className="text-xs text-slate-500 mb-2">
                Provide your final conclusion based on the investigation
              </p>
              <Textarea
                id="conclusion"
                value={formData.conclusion}
                onChange={(e) => updateField('conclusion', e.target.value)}
                rows={5}
                placeholder="State your final conclusion..."
                data-testid="findings-conclusion-input"
                className={error.includes('Conclusion') ? 'ring-2 ring-red-500' : ''}
              />
            </div>

            {/* Outcome & Recommendation - Side by Side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Outcome */}
              <div>
                <Label htmlFor="outcome" className="text-sm font-semibold text-slate-700 mb-2 block">
                  Outcome <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={formData.outcome}
                  onValueChange={(value) => updateField('outcome', value)}
                >
                  <SelectTrigger
                    id="outcome"
                    data-testid="findings-outcome-select"
                    className={error.includes('Outcome') ? 'ring-2 ring-red-500' : ''}
                  >
                    <SelectValue placeholder="Select outcome" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="genuine">Genuine</SelectItem>
                    <SelectItem value="suspicious">Suspicious</SelectItem>
                    <SelectItem value="unable_to_verify">Unable To Verify</SelectItem>
                    <SelectItem value="fraud_suspected">Fraud Suspected</SelectItem>
                    <SelectItem value="insufficient_evidence">Insufficient Evidence</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Recommendation */}
              <div>
                <Label htmlFor="recommendation" className="text-sm font-semibold text-slate-700 mb-2 block">
                  Recommendation <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={formData.recommendation}
                  onValueChange={(value) => updateField('recommendation', value)}
                >
                  <SelectTrigger
                    id="recommendation"
                    data-testid="findings-recommendation-select"
                    className={error.includes('Recommendation') ? 'ring-2 ring-red-500' : ''}
                  >
                    <SelectValue placeholder="Select recommendation" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="approve">Approve</SelectItem>
                    <SelectItem value="reject">Reject</SelectItem>
                    <SelectItem value="further_investigation">Further Investigation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Help Text */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <p className="text-xs text-blue-700">
              <strong>Note:</strong> All fields marked with <span className="text-red-500">*</span> are mandatory. 
              Ensure you have completed investigation activities and uploaded evidence before submitting.
            </p>
          </div>
        </div>

        {/* Sticky Footer */}
        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="border-slate-200"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!isFormComplete || isSubmitting}
            className="bg-brand-primary hover:bg-brand-primary/90"
            data-testid="submit-findings-confirm-button"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <FileText className="h-4 w-4 mr-2" />
                Submit Findings
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SubmitFindingsModal;
