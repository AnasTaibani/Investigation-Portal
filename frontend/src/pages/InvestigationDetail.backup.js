import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
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
  const [activeTab, setActiveTab] = useState('overview');
  const [evidenceByService, setEvidenceByService] = useState({});
  const [uploadingService, setUploadingService] = useState(null);
  const [findings, setFindings] = useState(null);
  const [activities, setActivities] = useState([]);
  const [showFindingsForm, setShowFindingsForm] = useState(false);
  const [showReworkForm, setShowReworkForm] = useState(false);

  // Form states
  const [findingsForm, setFindingsForm] = useState({
    summary: '',
    observations: '',
    findings: '',
    suspicion_indicators: '',
    conclusion: '',
    outcome: '',
    recommendation: '',
  });

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

  const handleFileUpload = async (serviceId, file, latitude, longitude, notes) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('service_id', serviceId);
      if (latitude) formData.append('latitude', latitude);
      if (longitude) formData.append('longitude', longitude);
      if (notes) formData.append('notes', notes);

      await uploadEvidence(investigationId, formData);
      toast.success('Evidence uploaded successfully');
      loadEvidenceForService(serviceId);
      loadInvestigation();
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

  const handleSubmitFindings = async () => {
    try {
      await submitFindings(investigationId, findingsForm);
      toast.success('Findings submitted successfully');
      setShowFindingsForm(false);
      loadInvestigation();
    } catch (error) {
      console.error('Error submitting findings:', error);
      toast.error('Failed to submit findings');
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
      assigned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-amber-100 text-amber-800',
      submitted: 'bg-green-100 text-green-800',
      rework_requested: 'bg-red-100 text-red-800',
      completed: 'bg-green-100 text-green-800',
      closed: 'bg-slate-100 text-slate-800',
    };
    return colors[status] || 'bg-slate-100 text-slate-800';
  };

  const canEdit = user?.role === 'investigator' && 
    investigation.assigned_investigator_id === user?.id &&
    !['completed', 'closed'].includes(investigation.status);

  return (
    <Layout>
      <div className="space-y-6" data-testid="investigation-detail-page">
        {/* Header */}
        <div className="flex items-center justify-between">
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
              <h1 className="text-[24px] font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
                {investigation.investigation_id}
              </h1>
              <p className="mt-1 text-[14px] text-slate-600">
                {investigation.insured_name} - {investigation.claim_number}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(investigation.status)}`}>
              {investigation.status.replace('_', ' ')}
            </span>
          </div>
        </div>

        {/* Case Info */}
        <div className="bg-white border border-slate-200 rounded-md shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Claim Number</p>
              <p className="mt-1 text-[14px] text-slate-900">{investigation.claim_number}</p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Policy Number</p>
              <p className="mt-1 text-[14px] text-slate-900">{investigation.policy_number}</p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Category</p>
              <p className="mt-1 text-[14px] text-slate-900">{investigation.category_name}</p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Sub Category</p>
              <p className="mt-1 text-[14px] text-slate-900">{investigation.sub_category_name}</p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Investigator</p>
              <p className="mt-1 text-[14px] text-slate-900">{investigation.investigator_name}</p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Assigned Date</p>
              <p className="mt-1 text-[14px] text-slate-900">
                {new Date(investigation.assigned_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Due Date</p>
              <p className="mt-1 text-[14px] text-slate-900">
                {new Date(investigation.due_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-[13px] font-medium text-slate-500 uppercase tracking-wider">Status</p>
              {canEdit && investigation.status === 'assigned' ? (
                <Button
                  onClick={() => handleStatusChange('in_progress')}
                  size="sm"
                  className="mt-1 bg-blue-700 text-white hover:bg-blue-800"
                  data-testid="start-investigation-button"
                >
                  Start Investigation
                </Button>
              ) : (
                <p className="mt-1 text-[14px] text-slate-900 capitalize">{investigation.status.replace('_', ' ')}</p>
              )}
            </div>
          </div>
        </div>

        {/* Assessor Notes */}
        {investigation.assessor_notes && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h3 className="text-[14px] font-medium text-blue-900 mb-2">Assessor Instructions</h3>
            <p className="text-[13px] text-blue-800">{investigation.assessor_notes}</p>
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-white border-b border-slate-200">
            <TabsTrigger value="overview" data-testid="tab-overview">Overview</TabsTrigger>
            <TabsTrigger value="services" data-testid="tab-services">Services</TabsTrigger>
            <TabsTrigger value="findings" data-testid="tab-findings">Findings</TabsTrigger>
            <TabsTrigger value="timeline" data-testid="tab-timeline">Timeline</TabsTrigger>
          </TabsList>

          {/* Services Tab */}
          <TabsContent value="services" className="space-y-4">
            <Accordion type="single" collapsible className="space-y-4">
              {investigation.services?.map((service) => (
                <AccordionItem
                  key={service.id}
                  value={service.id}
                  className="bg-white border border-slate-200 rounded-md shadow-sm"
                >
                  <AccordionTrigger className="px-6 py-4 hover:no-underline">
                    <div className="flex items-center justify-between w-full pr-4">
                      <div className="flex items-center gap-4">
                        <div>
                          <p className="text-[14px] font-medium text-slate-900">{service.service_name}</p>
                          <p className="text-[13px] text-slate-600 mt-1">{service.remarks}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(service.status)}`}>
                          {service.status}
                        </span>
                        <span className="text-[13px] text-slate-600">
                          {evidenceByService[service.id]?.length || 0} evidence
                        </span>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="px-6 pb-4 space-y-4">
                    {/* Service Actions */}
                    {canEdit && (
                      <div className="flex gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              size="sm"
                              variant="outline"
                              data-testid={`upload-evidence-${service.id}`}
                            >
                              <Upload className="h-4 w-4 mr-2" />
                              Upload Evidence
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Upload Evidence</DialogTitle>
                              <DialogDescription>
                                Upload evidence for {service.service_name}
                              </DialogDescription>
                            </DialogHeader>
                            <EvidenceUploadForm
                              serviceId={service.id}
                              onUpload={(file, lat, lng, notes) => handleFileUpload(service.id, file, lat, lng, notes)}
                            />
                          </DialogContent>
                        </Dialog>

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

          {/* Findings Tab */}
          <TabsContent value="findings" className="space-y-4">
            {findings ? (
              <div className="bg-white border border-slate-200 rounded-md shadow-sm p-6 space-y-4">
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Summary</h3>
                  <p className="mt-1 text-[13px] text-slate-900">{findings.summary}</p>
                </div>
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Observations</h3>
                  <p className="mt-1 text-[13px] text-slate-900">{findings.observations}</p>
                </div>
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Findings</h3>
                  <p className="mt-1 text-[13px] text-slate-900">{findings.findings}</p>
                </div>
                {findings.suspicion_indicators && (
                  <div>
                    <h3 className="text-[14px] font-medium text-slate-700">Suspicion Indicators</h3>
                    <p className="mt-1 text-[13px] text-slate-900">{findings.suspicion_indicators}</p>
                  </div>
                )}
                <div>
                  <h3 className="text-[14px] font-medium text-slate-700">Conclusion</h3>
                  <p className="mt-1 text-[13px] text-slate-900">{findings.conclusion}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <h3 className="text-[14px] font-medium text-slate-700">Outcome</h3>
                    <p className="mt-1 text-[13px] text-slate-900 capitalize">{findings.outcome}</p>
                  </div>
                  <div>
                    <h3 className="text-[14px] font-medium text-slate-700">Recommendation</h3>
                    <p className="mt-1 text-[13px] text-slate-900 capitalize">{findings.recommendation}</p>
                  </div>
                </div>

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

        {/* Findings Form Dialog */}
        <Dialog open={showFindingsForm} onOpenChange={setShowFindingsForm}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Submit Investigation Findings</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Summary</Label>
                <Textarea
                  value={findingsForm.summary}
                  onChange={(e) => setFindingsForm({ ...findingsForm, summary: e.target.value })}
                  rows={3}
                  data-testid="findings-summary-input"
                />
              </div>
              <div>
                <Label>Observations</Label>
                <Textarea
                  value={findingsForm.observations}
                  onChange={(e) => setFindingsForm({ ...findingsForm, observations: e.target.value })}
                  rows={3}
                  data-testid="findings-observations-input"
                />
              </div>
              <div>
                <Label>Findings</Label>
                <Textarea
                  value={findingsForm.findings}
                  onChange={(e) => setFindingsForm({ ...findingsForm, findings: e.target.value })}
                  rows={3}
                  data-testid="findings-findings-input"
                />
              </div>
              <div>
                <Label>Suspicion Indicators (Optional)</Label>
                <Textarea
                  value={findingsForm.suspicion_indicators}
                  onChange={(e) => setFindingsForm({ ...findingsForm, suspicion_indicators: e.target.value })}
                  rows={2}
                  data-testid="findings-suspicion-input"
                />
              </div>
              <div>
                <Label>Conclusion</Label>
                <Textarea
                  value={findingsForm.conclusion}
                  onChange={(e) => setFindingsForm({ ...findingsForm, conclusion: e.target.value })}
                  rows={3}
                  data-testid="findings-conclusion-input"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Outcome</Label>
                  <Select
                    value={findingsForm.outcome}
                    onValueChange={(value) => setFindingsForm({ ...findingsForm, outcome: value })}
                  >
                    <SelectTrigger data-testid="findings-outcome-select">
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
                <div>
                  <Label>Recommendation</Label>
                  <Select
                    value={findingsForm.recommendation}
                    onValueChange={(value) => setFindingsForm({ ...findingsForm, recommendation: value })}
                  >
                    <SelectTrigger data-testid="findings-recommendation-select">
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
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowFindingsForm(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSubmitFindings} data-testid="submit-findings-confirm-button">
                  Submit Findings
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

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
      </div>
    </Layout>
  );
};

// Evidence Upload Form Component
const EvidenceUploadForm = ({ serviceId, onUpload }) => {
  const [file, setFile] = useState(null);
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [notes, setNotes] = useState('');
  const [gettingLocation, setGettingLocation] = useState(false);

  const getLocation = () => {
    setGettingLocation(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toString());
          setLongitude(position.coords.longitude.toString());
          setGettingLocation(false);
          toast.success('Location captured');
        },
        (error) => {
          console.error('Error getting location:', error);
          toast.error('Failed to get location');
          setGettingLocation(false);
        }
      );
    } else {
      toast.error('Geolocation is not supported');
      setGettingLocation(false);
    }
  };

  const handleSubmit = () => {
    if (!file) {
      toast.error('Please select a file');
      return;
    }
    onUpload(file, latitude, longitude, notes);
  };

  return (
    <div className="space-y-4">
      <div>
        <Label>File</Label>
        <Input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="mt-1"
          data-testid="evidence-file-input"
        />
      </div>
      <div>
        <Label>Notes (Optional)</Label>
        <Textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          data-testid="evidence-notes-input"
        />
      </div>
      <div>
        <div className="flex items-center justify-between mb-2">
          <Label>Location (Optional)</Label>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={getLocation}
            disabled={gettingLocation}
            data-testid="capture-location-button"
          >
            <MapPin className="h-4 w-4 mr-2" />
            {gettingLocation ? 'Getting Location...' : 'Capture Location'}
          </Button>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Input
            type="number"
            step="any"
            placeholder="Latitude"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            data-testid="evidence-latitude-input"
          />
          <Input
            type="number"
            step="any"
            placeholder="Longitude"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            data-testid="evidence-longitude-input"
          />
        </div>
      </div>
      <div className="flex justify-end">
        <Button onClick={handleSubmit} data-testid="upload-evidence-confirm-button">
          <Upload className="h-4 w-4 mr-2" />
          Upload
        </Button>
      </div>
    </div>
  );
};

export default InvestigationDetail;
