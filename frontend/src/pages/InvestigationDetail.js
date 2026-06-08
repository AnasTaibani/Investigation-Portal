import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import EvidenceUploadModal from '../components/EvidenceUploadModal';
import SubmitFindingsModal from '../components/SubmitFindingsModal';
import EvidenceLibrary from '../components/EvidenceLibrary';
import {
  getInvestigation,
  getEvidence,
  uploadEvidence,
  updateService,
  submitFindings,
  getFindings,
  requestRework,
  getActivities,
  updateInvestigationStatus,
} from '../lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  FileText,
  Upload,
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Download,
  Send,
} from 'lucide-react';
import { toast } from 'sonner';

const InvestigationDetail = () => {
  const { investigationId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('services');
  const [evidenceByService, setEvidenceByService] = useState({});
  const [uploadingService, setUploadingService] = useState(null);
  const [findings, setFindings] = useState(null);
  const [activities, setActivities] = useState([]);
  const [showFindingsForm, setShowFindingsForm] = useState(false);
  const [showReworkForm, setShowReworkForm] = useState(false);

  const [reworkForm, setReworkForm] = useState({
    reason: '',
    additional_instructions: '',
    expected_deliverables: '',
  });

  useEffect(() => {
    loadInvestigation();
  }, [investigationId]);

  const loadInvestigation = async () => {
    try {
      const { data } = await getInvestigation(investigationId);
      setInvestigation(data);

      // Load evidence for each service
      if (data.services) {
        for (const service of data.services) {
          loadEvidenceForService(service.id);
        }
      }

      // Load findings
      try {
        const findingsRes = await getFindings(investigationId);
        setFindings(findingsRes.data);
      } catch (err) {
        // Findings may not exist yet
      }

      // Load activities
      const activitiesRes = await getActivities(investigationId);
      setActivities(activitiesRes.data);
    } catch (error) {
      console.error('Error loading investigation:', error);
      toast.error('Failed to load investigation details');
    } finally {
      setLoading(false);
    }
  };

  const loadEvidenceForService = async (serviceId) => {
    try {
      const { data } = await getEvidence(investigationId, serviceId);
      setEvidenceByService((prev) => ({ ...prev, [serviceId]: data }));
    } catch (error) {
      console.error('Error loading evidence:', error);
    }
  };

  const handleFileUpload = async (file, selectedServiceIds, latitude, longitude, notes) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('service_ids', selectedServiceIds.join(','));  // Comma-separated IDs
      if (latitude) formData.append('latitude', latitude);
      if (longitude) formData.append('longitude', longitude);
      if (notes) formData.append('notes', notes);

      await uploadEvidence(investigationId, formData);
      toast.success(`Evidence uploaded and linked to ${selectedServiceIds.length} service(s)`);
      
      // Small delay to ensure backend has updated
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Reload investigation first to update evidence counts
      await loadInvestigation();
      
      // Then reload evidence for all affected services
      for (const serviceId of selectedServiceIds) {
        await loadEvidenceForService(serviceId);
      }
      
      setUploadingService(null);
    } catch (error) {
      console.error('Error uploading evidence:', error);
      toast.error('Failed to upload evidence');
    }
  };

  const handleServiceStatusUpdate = async (serviceId, status, remarks) => {
    try {
      await updateService(investigationId, serviceId, { status, remarks });
      toast.success('Service updated successfully');
      loadInvestigation();
    } catch (error) {
      console.error('Error updating service:', error);
      toast.error('Failed to update service');
    }
  };

  const handleSubmitFindings = async (formData) => {
    try {
      await submitFindings(investigationId, formData);
      toast.success('Findings submitted successfully');
      setShowFindingsForm(false);
      // Reload investigation to show updated status and findings
      await loadInvestigation();
    } catch (error) {
      console.error('Error submitting findings:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit findings');
      throw error; // Re-throw so modal can handle it
    }
  };

  const handleRequestRework = async () => {
    try {
      await requestRework(investigationId, reworkForm);
      toast.success('Rework requested successfully');
      setShowReworkForm(false);
      loadInvestigation();
    } catch (error) {
      console.error('Error requesting rework:', error);
      toast.error('Failed to request rework');
    }
  };

  const handleStatusChange = async (newStatus) => {
    try {
      await updateInvestigationStatus(investigationId, newStatus);
      toast.success('Status updated successfully');
      loadInvestigation();
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Failed to update status');
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-700"></div>
        </div>
      </Layout>
    );
  }

  if (!investigation) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-slate-600">Investigation not found</p>
        </div>
      </Layout>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      assigned: 'bg-blue-50 text-blue-700 border-blue-200',
      in_progress: 'bg-amber-50 text-amber-700 border-amber-200',
      submitted: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      rework_requested: 'bg-red-50 text-red-700 border-red-200',
      completed: 'bg-green-50 text-green-700 border-green-200',
      closed: 'bg-slate-50 text-slate-700 border-slate-200',
    };
    return colors[status] || 'bg-slate-50 text-slate-700 border-slate-200';
  };

  const canEdit = user?.role === 'investigator' && 
    investigation.assigned_investigator_id === user?.id &&
    !['completed', 'closed'].includes(investigation.status);

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="space-y-6"
        data-testid="investigation-detail-page"
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="flex items-center justify-between"
        >
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate('/investigations')}
              variant="ghost"
              size="sm"
              data-testid="back-button"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl md:text-3xl font-heading font-semibold text-foreground tracking-tight">
                {investigation.investigation_id}
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                {investigation.insured_name} · {investigation.claim_number}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className={`px-4 py-1.5 rounded-xl text-sm font-medium border ${getStatusColor(investigation.status)}`}>
              {investigation.status.replace('_', ' ')}
            </span>
          </div>
        </motion.div>

        {/* Case Info */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="bg-card border-0 rounded-2xl shadow-premium p-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p className="label-text text-muted-foreground">Claim Number</p>
              <p className="mt-2 text-sm font-medium text-foreground">{investigation.claim_number}</p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Policy Number</p>
              <p className="mt-2 text-sm font-medium text-foreground">{investigation.policy_number}</p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Category</p>
              <p className="mt-2 text-sm font-medium text-foreground">{investigation.category_name}</p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Sub Category</p>
              <p className="mt-2 text-sm font-medium text-foreground">{investigation.sub_category_name}</p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Investigator</p>
              <p className="mt-2 text-sm font-medium text-foreground">{investigation.investigator_name}</p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Assigned Date</p>
              <p className="mt-2 text-sm font-medium text-foreground">
                {new Date(investigation.assigned_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Due Date</p>
              <p className="mt-2 text-sm font-medium text-foreground">
                {new Date(investigation.due_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="label-text text-muted-foreground">Status</p>
              {canEdit && investigation.status === 'assigned' ? (
                <Button
                  onClick={() => handleStatusChange('in_progress')}
                  size="sm"
                  className="mt-2"
                  data-testid="start-investigation-button"
                >
                  Start Investigation
                </Button>
              ) : (
                <p className="mt-2 text-sm font-medium text-foreground capitalize">{investigation.status.replace('_', ' ')}</p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Assessor Notes */}
        {investigation.assessor_notes && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
            className="bg-blue-50/50 border border-blue-100 rounded-2xl p-6 shadow-soft"
          >
            <h3 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Assessor Instructions
            </h3>
            <p className="text-sm text-blue-800 leading-relaxed">{investigation.assessor_notes}</p>
          </motion.div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-card border-0 p-1.5 shadow-premium rounded-xl">
            <TabsTrigger value="services" data-testid="tab-services" className="rounded-lg">
              Services
            </TabsTrigger>
            <TabsTrigger value="evidence" data-testid="tab-evidence" className="rounded-lg">
              Evidence Library
            </TabsTrigger>
            <TabsTrigger value="findings" data-testid="tab-findings" className="rounded-lg">
              Findings
            </TabsTrigger>
            <TabsTrigger value="timeline" data-testid="tab-timeline" className="rounded-lg">
              Timeline
            </TabsTrigger>
          </TabsList>

          {/* Services Tab */}
          <TabsContent value="services" className="space-y-4">
            <Accordion type="single" collapsible className="space-y-4">
              {investigation.services?.map((service) => (
                <AccordionItem
                  key={service.id}
                  value={service.id}
                  className="bg-card border-0 rounded-2xl shadow-premium mb-3 overflow-hidden"
                >
                  <AccordionTrigger className="px-6 py-5 hover:no-underline">
                    <div className="flex items-center justify-between w-full pr-4">
                      <div className="flex items-center gap-4">
                        <div>
                          <p className="text-base font-semibold text-foreground">{service.service_name}</p>
                          <p className="text-sm text-muted-foreground mt-1">{service.remarks}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(service.status)}`}>
                          {service.status}
                        </span>
                        {evidenceByService[service.id]?.length > 0 && (
                          <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 rounded-full text-xs font-medium">
                            📎 {evidenceByService[service.id]?.length}
                          </span>
                        )}
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4 space-y-4">
                    {/* Service Actions */}
                    {canEdit && (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setUploadingService(service)}
                          className="border-brand-primary text-brand-primary hover:bg-brand-primary hover:text-white"
                          data-testid={`upload-evidence-${service.id}`}
                        >
                          <Upload className="h-4 w-4 mr-2" />
                          Upload Evidence
                        </Button>

                        {service.status === 'pending' && (
                          <Button
                            size="sm"
                            onClick={() => handleServiceStatusUpdate(service.id, 'completed')}
                            data-testid={`complete-service-${service.id}`}
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Mark Complete
                          </Button>
                        )}
                      </div>
                    )}

                    {/* Evidence List */}
                    <div>
                      <h4 className="text-[13px] font-medium text-slate-700 mb-2">Evidence Files</h4>
                      {evidenceByService[service.id]?.length > 0 ? (
                        <div className="space-y-2">
                          {evidenceByService[service.id].map((evidence) => (
                            <div
                              key={evidence.id}
                              className="flex items-center justify-between p-3 bg-slate-50 rounded-md"
                            >
                              <div className="flex items-center gap-3">
                                <FileText className="h-5 w-5 text-slate-400" />
                                <div>
                                  <p className="text-[13px] text-slate-900">{evidence.original_filename}</p>
                                  {evidence.latitude && evidence.longitude && (
                                    <p className="text-[12px] text-slate-600 flex items-center gap-1">
                                      <MapPin className="h-3 w-3" />
                                      {evidence.latitude.toFixed(6)}, {evidence.longitude.toFixed(6)}
                                    </p>
                                  )}
                                </div>
                              </div>
                              <a
                                href={`${process.env.REACT_APP_BACKEND_URL}/api/evidence/${evidence.id}/download`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-700 hover:text-blue-800"
                                data-testid={`download-evidence-${evidence.id}`}
                              >
                                <Download className="h-4 w-4" />
                              </a>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-[13px] text-slate-500">No evidence uploaded yet</p>
                      )}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>

            {canEdit && investigation.status === 'in_progress' && (
              <div className="flex justify-end">
                <Button
                  onClick={() => setShowFindingsForm(true)}
                  className="bg-blue-700 text-white hover:bg-blue-800"
                  data-testid="submit-findings-button"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Submit Findings
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Evidence Library Tab */}
          <TabsContent value="evidence" className="space-y-4">
            <EvidenceLibrary 
              investigationId={investigationId} 
              services={investigation.services || []} 
            />
          </TabsContent>

          {/* Findings Tab */}
          <TabsContent value="findings" className="space-y-4">
            {findings ? (
              <div className="bg-card border-0 rounded-2xl shadow-premium p-6 space-y-6">
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Observations</h3>
                  <p className="mt-1 text-[13px] text-slate-900 whitespace-pre-wrap">{findings.observations}</p>
                </div>
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Conclusion</h3>
                  <p className="mt-1 text-[13px] text-slate-900 whitespace-pre-wrap">{findings.conclusion}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <h3 className="text-[14px] font-medium text-slate-700">Outcome</h3>
                    <p className="mt-1 text-[13px] text-slate-900 capitalize">{findings.outcome?.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <h3 className="text-[14px] font-medium text-slate-700">Recommendation</h3>
                    <p className="mt-1 text-[13px] text-slate-900 capitalize">{findings.recommendation?.replace('_', ' ')}</p>
                  </div>
                </div>

                {findings.submitted_by_name && (
                  <div className="pt-4 border-t text-xs text-slate-500">
                    Submitted by {findings.submitted_by_name} on {new Date(findings.submitted_at).toLocaleString()}
                  </div>
                )}

                {(user?.role === 'admin' || user?.role === 'assessor') && investigation.status === 'submitted' && (
                  <div className="flex gap-2 pt-4 border-t">
                    <Button
                      onClick={() => handleStatusChange('completed')}
                      className="bg-green-600 text-white hover:bg-green-700"
                      data-testid="approve-findings-button"
                    >
                      Approve
                    </Button>
                    <Button
                      onClick={() => setShowReworkForm(true)}
                      variant="outline"
                      data-testid="request-rework-button"
                    >
                      Request Rework
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white border border-slate-200 rounded-md shadow-sm p-12 text-center">
                <p className="text-slate-500">No findings submitted yet</p>
              </div>
            )}
          </TabsContent>

          {/* Timeline Tab */}
          <TabsContent value="timeline">
            <div className="bg-white border border-slate-200 rounded-md shadow-sm p-6">
              <div className="space-y-4">
                {activities.map((activity) => (
                  <div key={activity.id} className="flex gap-4">
                    <div className="flex-shrink-0">
                      <Clock className="h-5 w-5 text-slate-400" />
                    </div>
                    <div className="flex-1">
                      <p className="text-[13px] text-slate-900">{activity.description}</p>
                      <p className="text-[12px] text-slate-500 mt-1">
                        {activity.user_name} - {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* New Evidence Upload Modal */}
        {uploadingService && (
          <EvidenceUploadModal
            open={!!uploadingService}
            onClose={() => setUploadingService(null)}
            services={investigation.services || []}
            preselectedServiceId={uploadingService.id}
            onUpload={handleFileUpload}
          />
        )}

        {/* New Submit Findings Modal */}
        <SubmitFindingsModal
          open={showFindingsForm}
          onClose={() => setShowFindingsForm(false)}
          investigation={investigation}
          onSubmit={handleSubmitFindings}
        />

        {/* Rework Form Dialog */}
        <Dialog open={showReworkForm} onOpenChange={setShowReworkForm}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request Rework</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Reason</Label>
                <Textarea
                  value={reworkForm.reason}
                  onChange={(e) => setReworkForm({ ...reworkForm, reason: e.target.value })}
                  rows={3}
                  data-testid="rework-reason-input"
                />
              </div>
              <div>
                <Label>Additional Instructions</Label>
                <Textarea
                  value={reworkForm.additional_instructions}
                  onChange={(e) => setReworkForm({ ...reworkForm, additional_instructions: e.target.value })}
                  rows={3}
                  data-testid="rework-instructions-input"
                />
              </div>
              <div>
                <Label>Expected Deliverables</Label>
                <Textarea
                  value={reworkForm.expected_deliverables}
                  onChange={(e) => setReworkForm({ ...reworkForm, expected_deliverables: e.target.value })}
                  rows={2}
                  data-testid="rework-deliverables-input"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowReworkForm(false)}>
                  Cancel
                </Button>
                <Button onClick={handleRequestRework} data-testid="submit-rework-request-button">
                  Request Rework
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </motion.div>
    </Layout>
  );
};

export default InvestigationDetail;
