import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { getInvestigations, getDashboardStats } from '../lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  FolderOpen,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  TrendingDown,
  LayoutDashboard,
  Briefcase,
  Search,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const InvestigatorHome = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const [activeTab, setActiveTab] = useState(tabParam || 'workbench');
  const [assignedCases, setAssignedCases] = useState([]);
  const [allInvestigations, setAllInvestigations] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, assignedRes, allCasesRes] = await Promise.all([
        getDashboardStats(),
        getInvestigations({ limit: 1000, status: 'assigned' }), // ALL assigned cases
        getInvestigations({ limit: 100 }),
      ]);
      setStats(statsRes.data);
      setAssignedCases(assignedRes.data);
      setAllInvestigations(allCasesRes.data);
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
    return colors[status] || 'bg-slate-50 text-slate-700';
  };

  const statsCards = [
    { label: 'Assigned', value: stats?.assigned || 0, icon: FolderOpen, gradient: 'from-blue-500 to-blue-600', bgLight: 'bg-blue-50/50', iconColor: 'text-blue-600', trend: '+12%', trendUp: true },
    { label: 'In Progress', value: stats?.in_progress || 0, icon: Clock, gradient: 'from-amber-500 to-amber-600', bgLight: 'bg-amber-50/50', iconColor: 'text-amber-600', trend: '+8%', trendUp: true },
    { label: 'Submitted', value: stats?.submitted || 0, icon: FileCheck, gradient: 'from-emerald-500 to-emerald-600', bgLight: 'bg-emerald-50/50', iconColor: 'text-emerald-600', trend: '+16%', trendUp: true },
    { label: 'Rework Requested', value: stats?.rework_requested || 0, icon: AlertTriangle, gradient: 'from-red-500 to-red-600', bgLight: 'bg-red-50/50', iconColor: 'text-red-600', trend: '-5%', trendUp: false },
    { label: 'Completed', value: stats?.completed || 0, icon: CheckCircle2, gradient: 'from-green-500 to-green-600', bgLight: 'bg-green-50/50', iconColor: 'text-green-600', trend: '+20%', trendUp: true },
  ];

  const statusData = [
    { name: 'Assigned', value: stats?.assigned || 0, color: '#1976D2' },
    { name: 'In Progress', value: stats?.in_progress || 0, color: '#42A5F5' },
    { name: 'Submitted', value: stats?.submitted || 0, color: '#90CAF9' },
    { name: 'Completed', value: stats?.completed || 0, color: '#1565C0' },
  ];

  const barData = [
    { name: 'Assigned', value: stats?.assigned || 0 },
    { name: 'In Progress', value: stats?.in_progress || 0 },
    { name: 'Submitted', value: stats?.submitted || 0 },
    { name: 'Completed', value: stats?.completed || 0 },
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-xl p-3 shadow-premium">
          <p className="text-sm font-medium text-foreground">{payload[0].name}</p>
          <p className="text-lg font-bold text-primary">{payload[0].value}</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="h-8 w-48 bg-slate-200 animate-pulse rounded-lg"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-32 bg-slate-200 animate-pulse rounded-2xl"></div>
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
        data-testid="investigator-home-page"
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl font-heading font-semibold text-foreground tracking-tight">
            Welcome back, {user?.name}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage your investigation cases and track progress
          </p>
        </motion.div>

        {/* Premium Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-card border-0 p-1.5 shadow-premium rounded-xl">
            <TabsTrigger 
              value="workbench"
              className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              data-testid="tab-workbench"
            >
              <Briefcase className="h-4 w-4 mr-2" />
              Workbench
            </TabsTrigger>
            <TabsTrigger 
              value="investigations"
              className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              data-testid="tab-investigations"
            >
              <Search className="h-4 w-4 mr-2" />
              Investigation Enquiry
            </TabsTrigger>
            <TabsTrigger 
              value="dashboard"
              className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              data-testid="tab-dashboard"
            >
              <LayoutDashboard className="h-4 w-4 mr-2" />
              Dashboard
            </TabsTrigger>
          </TabsList>

          {/* Workbench Tab */}
          <TabsContent value="workbench" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-xl font-heading font-semibold text-foreground mb-4">
                All Assigned Cases
              </h2>
              <div className="space-y-3">
                {assignedCases.length > 0 ? (
                  assignedCases.map((investigation, index) => (
                    <motion.div
                      key={investigation.investigation_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05, duration: 0.3 }}
                      className="bg-card border-0 rounded-2xl shadow-premium p-6 hover:shadow-premium-hover transition-all cursor-pointer"
                      onClick={() => navigate(`/investigations/${investigation.investigation_id}`)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-foreground">
                              {investigation.investigation_id}
                            </h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(investigation.status)}`}>
                              {investigation.status.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-3">
                            {investigation.insured_name} · {investigation.claim_number}
                          </p>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <p className="label-text text-muted-foreground">Category</p>
                              <p className="mt-1 font-medium text-foreground">{investigation.category_name}</p>
                            </div>
                            <div>
                              <p className="label-text text-muted-foreground">Assigned Date</p>
                              <p className="mt-1 font-medium text-foreground">
                                {new Date(investigation.assigned_date).toLocaleDateString()}
                              </p>
                            </div>
                            <div>
                              <p className="label-text text-muted-foreground">Due Date</p>
                              <p className="mt-1 font-medium text-foreground">
                                {new Date(investigation.due_date).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="flex items-end justify-end">
                              <Button size="sm" className="bg-primary hover:bg-primary/90">
                                View Details
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <div className="text-center py-12 bg-card rounded-2xl">
                    <Briefcase className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
                    <p className="text-muted-foreground">No assigned cases</p>
                  </div>
                )}
              </div>
            </motion.div>
          </TabsContent>

          {/* Investigation Enquiry Tab */}
          <TabsContent value="investigations" className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-card border-0 rounded-2xl shadow-premium overflow-hidden"
            >
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-lg font-heading font-semibold text-foreground">
                  All Investigations
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Investigation ID
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Claim Number
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Insured Name
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Assigned Date
                      </th>
                      <th className="px-6 py-4 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {allInvestigations.map((investigation) => (
                      <tr key={investigation.investigation_id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-foreground">
                            {investigation.investigation_id}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-muted-foreground">
                            {investigation.claim_number}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-foreground">
                            {investigation.insured_name}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(investigation.status)}`}>
                            {investigation.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                          {new Date(investigation.assigned_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => navigate(`/investigations/${investigation.investigation_id}`)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </TabsContent>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {statsCards.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.4 }}
                  className={`bg-card border-0 rounded-2xl p-6 shadow-premium ${stat.bgLight}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="label-text text-muted-foreground">{stat.label}</p>
                      <p className="mt-3 text-4xl font-heading font-bold text-foreground tracking-tighter">
                        {stat.value}
                      </p>
                      <div className="mt-3 flex items-center gap-1.5">
                        {stat.trendUp ? (
                          <TrendingUp className="h-4 w-4 text-green-600" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-600" />
                        )}
                        <span className={`text-sm font-medium ${stat.trendUp ? 'text-green-600' : 'text-red-600'}`}>
                          {stat.trend}
                        </span>
                        <span className="text-xs text-muted-foreground">vs last month</span>
                      </div>
                    </div>
                    <div className={`p-3 rounded-xl ${stat.iconColor} bg-white/50 backdrop-blur-sm`}>
                      <stat.icon className="h-6 w-6" strokeWidth={2.5} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6, duration: 0.4 }}
                className="bg-card border-0 rounded-2xl shadow-premium p-6"
              >
                <h2 className="text-lg font-heading font-semibold text-foreground mb-6">
                  Cases by Status
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7, duration: 0.4 }}
                className="bg-card border-0 rounded-2xl shadow-premium p-6"
              >
                <h2 className="text-lg font-heading font-semibold text-foreground mb-6">
                  Status Overview
                </h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                    <XAxis 
                      dataKey="name" 
                      tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                      axisLine={{ stroke: 'hsl(var(--border))' }}
                    />
                    <YAxis 
                      tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                      axisLine={{ stroke: 'hsl(var(--border))' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="value" fill="#1976D2" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </motion.div>
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>
    </Layout>
  );
};

export default InvestigatorHome;
