import React, { useState, useCallback } from 'react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Upload, MapPin, X, FileImage, Loader2, CheckSquare, Square } from 'lucide-react';

const EvidenceUploadModal = ({ open, onClose, services = [], preselectedServiceId = null, onUpload }) => {
  const [file, setFile] = useState(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedServices, setSelectedServices] = useState(preselectedServiceId ? [preselectedServiceId] : []);
  const [gettingLocation, setGettingLocation] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const toggleService = (serviceId) => {
    setSelectedServices(prev => 
      prev.includes(serviceId) 
        ? prev.filter(id => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const getLocation = () => {
    setGettingLocation(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toString());
          setLongitude(position.coords.longitude.toString());
          setGettingLocation(false);
          toast.success('Location captured successfully');
        },
        (error) => {
          console.error('Error getting location:', error);
          toast.error('Failed to get location');
          setGettingLocation(false);
        }
      );
    } else {
      toast.error('Geolocation is not supported by your browser');
      setGettingLocation(false);
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }

    if (selectedServices.length === 0) {
      toast.error('Please select at least one service');
      return;
    }

    setIsUploading(true);
    try {
      await onUpload(file, selectedServices, latitude, longitude, notes);
      // Reset form
      setFile(null);
      setLatitude('');
      setLongitude('');
      setNotes('');
      setSelectedServices(preselectedServiceId ? [preselectedServiceId] : []);
      onClose();
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCancel = () => {
    setFile(null);
    setLatitude('');
    setLongitude('');
    setNotes('');
    setSelectedServices(preselectedServiceId ? [preselectedServiceId] : []);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-heading">Upload Evidence</DialogTitle>
          <DialogDescription className="text-sm text-slate-500">
            Upload evidence and link to one or more services
          </DialogDescription>
        </DialogHeader>

        {/* Scrollable Body */}
        <div className="px-8 py-6 space-y-6 overflow-y-auto max-h-[60vh] custom-scrollbar">
          {/* File Upload Dropzone */}
          <div>
            <Label className="text-sm font-medium text-slate-700 mb-3 block">Evidence File *</Label>
            <div
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-10 transition-all ${
                isDragActive
                  ? 'border-brand-primary bg-brand-primary/5'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300'
              }`}
              data-testid="evidence-dropzone"
            >
              <input
                type="file"
                id="file-upload"
                onChange={handleFileSelect}
                className="hidden"
                accept="image/*,video/*,.pdf,.doc,.docx"
                data-testid="evidence-file-input"
              />
              
              {!file ? (
                <label
                  htmlFor="file-upload"
                  className="flex flex-col items-center justify-center cursor-pointer"
                >
                  <Upload className="h-12 w-12 text-slate-400 mb-4" />
                  <p className="text-sm font-medium text-slate-700 mb-1">
                    Drop your file here or click to browse
                  </p>
                  <p className="text-xs text-slate-500">
                    Supports: Images, Videos, PDF, Documents
                  </p>
                </label>
              ) : (
                <div className="flex items-center justify-between bg-white rounded-xl p-4 shadow-soft">
                  <div className="flex items-center gap-3">
                    <FileImage className="h-10 w-10 text-brand-primary" />
                    <div>
                      <p className="text-sm font-medium text-slate-900">{file.name}</p>
                      <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
                    data-testid="remove-file-button"
                  >
                    <X className="h-5 w-5 text-slate-400" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Service Selection */}
          <div>
            <Label className="text-sm font-medium text-slate-700 mb-3 block">
              Link to Services * <span className="text-xs text-slate-500 font-normal">(Select one or more)</span>
            </Label>
            <div className="bg-slate-50 rounded-xl p-4 space-y-2">
              {services.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-2">No services available</p>
              ) : (
                services.map((service) => (
                  <button
                    key={service.id}
                    type="button"
                    onClick={() => toggleService(service.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                      selectedServices.includes(service.id)
                        ? 'border-brand-primary bg-brand-primary/5'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                    data-testid={`service-checkbox-${service.id}`}
                  >
                    {selectedServices.includes(service.id) ? (
                      <CheckSquare className="h-5 w-5 text-brand-primary flex-shrink-0" />
                    ) : (
                      <Square className="h-5 w-5 text-slate-400 flex-shrink-0" />
                    )}
                    <div className="flex-1 text-left">
                      <p className="text-sm font-medium text-slate-900">{service.service_name}</p>
                      {service.remarks && (
                        <p className="text-xs text-slate-500 mt-0.5">{service.remarks}</p>
                      )}
                    </div>
                    {selectedServices.includes(service.id) && (
                      <span className="text-xs px-2 py-0.5 bg-brand-primary/10 text-brand-primary rounded-full">
                        Selected
                      </span>
                    )}
                  </button>
                ))
              )}
            </div>
            {selectedServices.length > 0 && (
              <p className="text-xs text-slate-600 mt-2">
                {selectedServices.length} service{selectedServices.length > 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          {/* Notes Section */}
          <div>
            <Label htmlFor="notes" className="text-sm font-medium text-slate-700 mb-3 block">
              Notes <span className="text-slate-400 font-normal">(Optional)</span>
            </Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder="Add any relevant notes or context about this evidence..."
              data-testid="evidence-notes-input"
            />
          </div>

          {/* Location Section */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-sm font-medium text-slate-700">
                Location <span className="text-slate-400 font-normal">(Optional)</span>
              </Label>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={getLocation}
                disabled={gettingLocation}
                className="border-slate-200 hover:bg-slate-50"
                data-testid="capture-location-button"
              >
                <MapPin className="h-4 w-4 mr-2" />
                {gettingLocation ? 'Capturing...' : 'Capture Location'}
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="latitude" className="text-xs text-slate-500 mb-2 block">
                  Latitude
                </Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  placeholder="e.g., 19.0760"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  data-testid="evidence-latitude-input"
                />
              </div>
              <div>
                <Label htmlFor="longitude" className="text-xs text-slate-500 mb-2 block">
                  Longitude
                </Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  placeholder="e.g., 72.8777"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  data-testid="evidence-longitude-input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Sticky Footer */}
        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isUploading}
            className="border-slate-200"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!file || selectedServices.length === 0 || isUploading}
            className="bg-brand-primary hover:bg-brand-primary/90"
            data-testid="upload-evidence-confirm-button"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Upload Evidence
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EvidenceUploadModal;
