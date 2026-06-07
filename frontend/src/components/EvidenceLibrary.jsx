import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getEvidenceLibrary, updateEvidenceLinks } from '../lib/api';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { FileImage, Download, Link2, Calendar, User, MapPin, FileText, CheckSquare, Square } from 'lucide-react';
import { toast } from 'sonner';

const EvidenceLibrary = ({ investigationId, services = [] }) => {
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingEvidence, setEditingEvidence] = useState(null);
  const [selectedServices, setSelectedServices] = useState([]);

  useEffect(() => {
    loadEvidence();
  }, [investigationId]);

  const loadEvidence = async () => {
    try {
      const { data } = await getEvidenceLibrary(investigationId);
      setEvidence(data);
    } catch (error) {
      console.error('Error loading evidence library:', error);
      toast.error('Failed to load evidence library');
    } finally {
      setLoading(false);
    }
  };

  const handleEditLinks = (evidenceItem) => {
    setEditingEvidence(evidenceItem);
    setSelectedServices(evidenceItem.linked_services || []);
  };

  const toggleService = (serviceId) => {
    setSelectedServices(prev =>
      prev.includes(serviceId)
        ? prev.filter(id => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleSaveLinks = async () => {
    try {
      await updateEvidenceLinks(editingEvidence.id, selectedServices);
      toast.success('Evidence service links updated');
      setEditingEvidence(null);
      loadEvidence();
    } catch (error) {
      console.error('Error updating evidence links:', error);
      toast.error('Failed to update evidence links');
    }
  };

  const handleDownload = (evidence) => {
    const downloadUrl = `${process.env.REACT_APP_BACKEND_URL}/api/evidence/${evidence.id}/download`;
    window.open(downloadUrl, '_blank');
  };

  const getFileIcon = (contentType) => {
    if (contentType?.startsWith('image/')) return '🖼️';
    if (contentType?.startsWith('video/')) return '🎥';
    if (contentType?.includes('pdf')) return '📄';
    return '📎';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-heading font-semibold text-slate-900">Evidence Library</h3>
          <p className="text-sm text-slate-600 mt-1">
            {evidence.length} evidence item{evidence.length !== 1 ? 's' : ''} uploaded
          </p>
        </div>
      </div>

      {evidence.length === 0 ? (
        <div className="text-center py-12 bg-slate-50 rounded-2xl">
          <FileImage className="h-12 w-12 mx-auto text-slate-400 mb-3" />
          <p className="text-slate-600">No evidence uploaded yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {evidence.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-2xl shadow-premium p-6 hover:shadow-premium-hover transition-all"
            >
              <div className="flex items-start gap-4">
                {/* File Icon */}
                <div className="flex-shrink-0 w-16 h-16 bg-slate-100 rounded-xl flex items-center justify-center text-3xl">
                  {getFileIcon(item.content_type)}
                </div>

                {/* File Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h4 className="text-base font-semibold text-slate-900 truncate">
                        {item.original_filename}
                      </h4>
                      <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          {item.uploaded_by_name}
                        </span>
                        <span className="flex items-center gap-1">
                          <FileText className="h-3 w-3" />
                          {(item.size / 1024).toFixed(2)} KB
                        </span>
                        {(item.latitude || item.longitude) && (
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            Location attached
                          </span>
                        )}
                      </div>

                      {/* Notes */}
                      {item.notes && (
                        <p className="text-sm text-slate-600 mt-3 p-3 bg-slate-50 rounded-lg">
                          {item.notes}
                        </p>
                      )}

                      {/* Linked Services */}
                      <div className="mt-3">
                        <p className="text-xs font-medium text-slate-700 mb-2">Linked Services:</p>
                        <div className="flex flex-wrap gap-2">
                          {item.linked_service_details && item.linked_service_details.length > 0 ? (
                            item.linked_service_details.map((service) => (
                              <span
                                key={service.id}
                                className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
                              >
                                {service.name}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-slate-500">No services linked</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownload(item)}
                        className="border-slate-200"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleEditLinks(item)}
                        className="border-brand-primary text-brand-primary hover:bg-brand-primary hover:text-white"
                      >
                        <Link2 className="h-4 w-4 mr-2" />
                        Manage Links
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Edit Links Modal */}
      {editingEvidence && (
        <Dialog open={!!editingEvidence} onOpenChange={() => setEditingEvidence(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="text-xl font-heading">Manage Service Links</DialogTitle>
              <p className="text-sm text-slate-500 mt-2">
                {editingEvidence.original_filename}
              </p>
            </DialogHeader>

            <div className="px-8 py-6 space-y-4">
              <p className="text-sm text-slate-700">
                Select which services this evidence supports:
              </p>
              <div className="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar">
                {services.map((service) => (
                  <button
                    key={service.id}
                    type="button"
                    onClick={() => toggleService(service.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                      selectedServices.includes(service.id)
                        ? 'border-brand-primary bg-brand-primary/5'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
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
                ))}
              </div>
              <p className="text-xs text-slate-600">
                {selectedServices.length} service{selectedServices.length !== 1 ? 's' : ''} selected
              </p>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setEditingEvidence(null)}
                className="border-slate-200"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveLinks}
                className="bg-brand-primary hover:bg-brand-primary/90"
              >
                Save Changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default EvidenceLibrary;
