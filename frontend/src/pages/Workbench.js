import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { getInvestigations } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Briefcase, ArrowRight, Calendar, User, FileText, Tag } from 'lucide-react';

const Workbench = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [assignedCases, setAssignedCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const assignedRes = await getInvestigations({ limit: 1000, status: 'assigned' });
      setAssignedCases(assignedRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="h-8 w-48 bg-slate-200 animate-pulse rounded-lg"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-slate-200 animate-pulse rounded-2xl"></div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        className="space-y-6"
        data-testid="workbench-page"
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl font-heading font-semibold text-slate-900 tracking-tight">
            Workbench
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            {assignedCases.length} assigned investigation case{assignedCases.length !== 1 ? 's' : ''}
          </p>
        </motion.div>

        {/* Assigned Cases */}
        <div className="space-y-4">
          {assignedCases.length > 0 ? (
            assignedCases.map((investigation, index) => (
              <motion.div
                key={investigation.investigation_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05, duration: 0.3 }}
                className="group bg-white border-0 rounded-2xl shadow-premium p-6 hover:shadow-premium-hover transition-all cursor-pointer relative overflow-hidden"
                onClick={() => navigate(`/investigations/${investigation.investigation_id}`)}
              >
                {/* Subtle hover indicator */}
                <div className="absolute inset-0 bg-gradient-to-r from-brand-primary/0 to-brand-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                
                <div className="relative flex items-start justify-between gap-6">
                  {/* Main Content */}
                  <div className="flex-1 space-y-4">
                    {/* Investigation ID & Status */}
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-xl font-semibold text-slate-900 tracking-tight">
                        {investigation.investigation_id}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(investigation.status)}`}>
                        {investigation.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>

                    {/* Claimant & Claim Number - Prominent */}
                    <div className="flex items-center gap-2 text-base">
                      <User className="h-4 w-4 text-slate-400 flex-shrink-0" />
                      <span className="font-semibold text-slate-800">{investigation.insured_name}</span>
                      <span className="text-slate-400">·</span>
                      <FileText className="h-4 w-4 text-slate-400 flex-shrink-0" />
                      <span className="font-medium text-slate-700">{investigation.claim_number}</span>
                    </div>

                    {/* Metadata Grid - Clear Visual Hierarchy */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      {/* Category */}
                      <div className="flex items-start gap-2">
                        <Tag className="h-4 w-4 text-slate-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-0.5">
                            Category
                          </p>
                          <p className="text-sm font-semibold text-slate-900">
                            {investigation.category_name || 'Not specified'}
                          </p>
                        </div>
                      </div>

                      {/* Assigned Date */}
                      <div className="flex items-start gap-2">
                        <Calendar className="h-4 w-4 text-slate-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-0.5">
                            Assigned
                          </p>
                          <p className="text-sm font-semibold text-slate-900">
                            {new Date(investigation.assigned_date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </p>
                        </div>
                      </div>

                      {/* Due Date */}
                      <div className="flex items-start gap-2">
                        <Calendar className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-0.5">
                            Due Date
                          </p>
                          <p className="text-sm font-semibold text-slate-900">
                            {new Date(investigation.due_date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Button - Highly Visible */}
                  <div className="flex-shrink-0 flex items-center">
                    <Button 
                      size="lg" 
                      className="bg-brand-primary hover:bg-brand-deep text-white shadow-premium group-hover:shadow-premium-hover transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/investigations/${investigation.investigation_id}`);
                      }}
                    >
                      <span className="font-semibold">View Details</span>
                      <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-16 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200"
            >
              <Briefcase className="h-16 w-16 mx-auto text-slate-300 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 mb-2">No Assigned Cases</h3>
              <p className="text-sm text-slate-500">You don't have any investigations assigned yet.</p>
            </motion.div>
          )}
        </div>
      </motion.div>
    </Layout>
  );
};

export default Workbench;
