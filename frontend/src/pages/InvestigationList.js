import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { getInvestigations } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, Plus, Filter } from 'lucide-react';

const InvestigationList = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadInvestigations();
  }, [statusFilter]);

  const loadInvestigations = async () => {
    try {
      const params = {};
      if (statusFilter && statusFilter !== 'all') params.status = statusFilter;
      const { data } = await getInvestigations(params);
      setInvestigations(data);
    } catch (error) {
      console.error('Error loading investigations:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredInvestigations = investigations.filter((inv) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      inv.investigation_id.toLowerCase().includes(searchLower) ||
      inv.claim_number.toLowerCase().includes(searchLower) ||
      inv.policy_number.toLowerCase().includes(searchLower) ||
      inv.insured_name.toLowerCase().includes(searchLower)
    );
  });

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

  return (
    <Layout>
      <div className="space-y-6" data-testid="investigation-list-page">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-semibold text-slate-900 tracking-tight">
              Investigations
            </h1>
            <p className="mt-2 text-sm text-slate-600">
              Manage and track all investigation cases
            </p>
          </div>
          {(user?.role === 'admin' || user?.role === 'assessor') && (
            <Button
              onClick={() => navigate('/investigations/create')}
              className="bg-brand-primary hover:bg-brand-primary/90 text-white"
              data-testid="create-investigation-button"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Investigation
            </Button>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-premium p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="search" className="text-sm font-medium text-slate-700 mb-2 block">
                Search
              </Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  id="search"
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                  placeholder="Search by ID, claim, policy, or name..."
                  data-testid="search-investigations-input"
                />
              </div>
            </div>

            <div>
              <Label className="text-sm font-medium text-slate-700 mb-2 block">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger data-testid="status-filter-select">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="assigned">Assigned</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="submitted">Submitted</SelectItem>
                  <SelectItem value="rework_requested">Rework Requested</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                }}
                variant="outline"
                className="border-slate-200"
                data-testid="clear-filters-button"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-premium overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm" data-testid="investigations-table">
                <thead className="bg-slate-50/50">
                  <tr>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Investigation ID</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Claim Number</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Policy Number</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Insured Name</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Status</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Assigned Date</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Due Date</th>
                    <th className="py-4 px-6 font-semibold text-slate-700 text-xs uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="text-slate-600">
                  {filteredInvestigations.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="py-12 px-6 text-center text-slate-500">
                        No investigations found
                      </td>
                    </tr>
                  ) : (
                    filteredInvestigations.map((item, index) => (
                      <tr 
                        key={item.id} 
                        className={`hover:bg-slate-50 transition-colors cursor-pointer ${index % 2 === 0 ? '' : 'bg-slate-50/30'}`}
                        onClick={() => navigate(`/investigations/${item.investigation_id}`)}
                      >
                        <td className="py-4 px-6 border-b border-slate-100 font-medium text-slate-900">
                          {item.investigation_id}
                        </td>
                        <td className="py-4 px-6 border-b border-slate-100">{item.claim_number}</td>
                        <td className="py-4 px-6 border-b border-slate-100">{item.policy_number}</td>
                        <td className="py-4 px-6 border-b border-slate-100">{item.insured_name}</td>
                        <td className="py-4 px-6 border-b border-slate-100">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                            {item.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-4 px-6 border-b border-slate-100">
                          {new Date(item.assigned_date).toLocaleDateString()}
                        </td>
                        <td className="py-4 px-6 border-b border-slate-100">
                          {new Date(item.due_date).toLocaleDateString()}
                        </td>
                        <td className="py-4 px-6 border-b border-slate-100">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/investigations/${item.investigation_id}`);
                            }}
                            className="text-brand-primary hover:text-brand-primary/80 font-medium transition-colors"
                            data-testid={`view-investigation-${item.investigation_id}`}
                          >
                            View →
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default InvestigationList;
