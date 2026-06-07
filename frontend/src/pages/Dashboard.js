import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { getDashboardStats, getInvestigations } from '../lib/api';
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
  Legend,
} from 'recharts';
import {
  FolderOpen,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileCheck,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentCases, setRecentCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, casesRes] = await Promise.all([
        getDashboardStats(),
        getInvestigations({ limit: 5 }),
      ]);
      setStats(statsRes.data);
      setRecentCases(casesRes.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  // Loading skeleton
  if (loading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="h-8 w-48 bg-slate-200 animate-pulse rounded-lg"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-32 bg-slate-200 animate-pulse rounded-2xl"></div>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      assigned: 'bg-blue-100 text-blue-700',
      in_progress: 'bg-amber-100 text-amber-700',
      submitted: 'bg-emerald-100 text-emerald-700',
      rework_requested: 'bg-red-100 text-red-700',
      completed: 'bg-green-100 text-green-700',
      closed: 'bg-slate-100 text-slate-700',
      cancelled: 'bg-slate-100 text-slate-700',
    };
    return colors[status] || 'bg-slate-100 text-slate-700';
  };

  // Premium stat cards with gradients
  const statsCards = user?.role === 'investigator'
    ? [
        { 
          label: 'Assigned', 
          value: stats?.assigned || 0, 
          icon: FolderOpen, 
          gradient: 'from-blue-500 to-blue-600',
          bgLight: 'bg-blue-50/50',
          bgDark: '',
          iconColor: 'text-blue-600 ',
          trend: '+12%',
          trendUp: true
        },
        { 
          label: 'In Progress', 
          value: stats?.in_progress || 0, 
          icon: Clock, 
          gradient: 'from-amber-500 to-amber-600',
          bgLight: 'bg-amber-50/50',
          bgDark: '',
          iconColor: 'text-amber-600 ',
          trend: '+8%',
          trendUp: true
        },
        { 
          label: 'Submitted', 
          value: stats?.submitted || 0, 
          icon: FileCheck, 
          gradient: 'from-emerald-500 to-emerald-600',
          bgLight: 'bg-emerald-50/50',
          bgDark: '',
          iconColor: 'text-emerald-600 ',
          trend: '+16%',
          trendUp: true
        },
        { 
          label: 'Rework Requested', 
          value: stats?.rework_requested || 0, 
          icon: AlertTriangle, 
          gradient: 'from-red-500 to-red-600',
          bgLight: 'bg-red-50/50',
          bgDark: '',
          iconColor: 'text-red-600 ',
          trend: '-5%',
          trendUp: false
        },
        { 
          label: 'Completed', 
          value: stats?.completed || 0, 
          icon: CheckCircle2, 
          gradient: 'from-green-500 to-green-600',
          bgLight: 'bg-green-50/50',
          bgDark: '',
          iconColor: 'text-green-600 ',
          trend: '+20%',
          trendUp: true
        },
        { 
          label: 'Closed', 
          value: stats?.closed || 0, 
          icon: XCircle, 
          gradient: 'from-slate-500 to-slate-600',
          bgLight: 'bg-slate-50/50',
          bgDark: '',
          iconColor: 'text-slate-600 ',
          trend: '+10%',
          trendUp: true
        },
      ]
    : [
        { 
          label: 'Total Cases', 
          value: stats?.total || 0, 
          icon: FolderOpen, 
          gradient: 'from-blue-500 to-blue-600',
          bgLight: 'bg-blue-50/50',
          bgDark: '',
          iconColor: 'text-blue-600 ',
          trend: '+18%',
          trendUp: true
        },
        { 
          label: 'Assigned', 
          value: stats?.assigned || 0, 
          icon: Clock, 
          gradient: 'from-amber-500 to-amber-600',
          bgLight: 'bg-amber-50/50',
          bgDark: '',
          iconColor: 'text-amber-600 ',
          trend: '+12%',
          trendUp: true
        },
        { 
          label: 'In Progress', 
          value: stats?.in_progress || 0, 
          icon: Clock, 
          gradient: 'from-orange-500 to-orange-600',
          bgLight: 'bg-orange-50/50',
          bgDark: '',
          iconColor: 'text-orange-600 ',
          trend: '+8%',
          trendUp: true
        },
        { 
          label: 'Submitted', 
          value: stats?.submitted || 0, 
          icon: FileCheck, 
          gradient: 'from-emerald-500 to-emerald-600',
          bgLight: 'bg-emerald-50/50',
          bgDark: '',
          iconColor: 'text-emerald-600 ',
          trend: '+16%',
          trendUp: true
        },
        { 
          label: 'Completed', 
          value: stats?.completed || 0, 
          icon: CheckCircle2, 
          gradient: 'from-green-500 to-green-600',
          bgLight: 'bg-green-50/50',
          bgDark: '',
          iconColor: 'text-green-600 ',
          trend: '+20%',
          trendUp: true
        },
        { 
          label: 'Closed', 
          value: stats?.closed || 0, 
          icon: XCircle, 
          gradient: 'from-slate-500 to-slate-600',
          bgLight: 'bg-slate-50/50',
          bgDark: '',
          iconColor: 'text-slate-600 ',
          trend: '+10%',
          trendUp: true
        },
      ];

  // Chart data with MetaMorphoSys brand colors
  const statusData = [
    { name: 'Assigned', value: stats?.assigned || 0, color: '#1976D2' },      // Deep Blue
    { name: 'In Progress', value: stats?.in_progress || 0, color: '#42A5F5' }, // Sky Blue
    { name: 'Submitted', value: stats?.submitted || 0, color: '#90CAF9' },     // Light Blue
    { name: 'Completed', value: stats?.completed || 0, color: '#1565C0' },     // Darker Blue
  ];

  const barData = [
    { name: 'Assigned', value: stats?.assigned || 0 },
    { name: 'In Progress', value: stats?.in_progress || 0 },
    { name: 'Submitted', value: stats?.submitted || 0 },
    { name: 'Completed', value: stats?.completed || 0 },
  ];

  // Custom tooltip for charts
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

  return (
    <Layout>
      <div className="space-y-8" data-testid="dashboard-page">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl font-heading font-semibold text-foreground tracking-tight">
            Dashboard
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Welcome back, {user?.name}. Here's an overview of your investigation cases.
          </p>
        </motion.div>

        {/* Premium Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statsCards.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.4 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className={`group relative overflow-hidden bg-card border-0 rounded-2xl p-6 shadow-premium hover:shadow-premium-hover transition-all cursor-pointer ${stat.bgLight} ${stat.bgDark}`}
              data-testid={`stat-card-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              {/* Gradient overlay on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
              
              <div className="relative flex items-start justify-between">
                <div className="flex-1">
                  <p className="label-text text-muted-foreground">{stat.label}</p>
                  <p className="mt-3 text-4xl font-heading font-bold text-foreground tracking-tighter">
                    {stat.value}
                  </p>
                  
                  {/* Trend indicator */}
                  <div className="mt-3 flex items-center gap-1.5">
                    {stat.trendUp ? (
                      <TrendingUp className="h-4 w-4 text-green-600 " />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-600 " />
                    )}
                    <span className={`text-sm font-medium ${stat.trendUp ? 'text-green-600 ' : 'text-red-600 '}`}>
                      {stat.trend}
                    </span>
                    <span className="text-xs text-muted-foreground">vs last month</span>
                  </div>
                </div>
                
                {/* Icon */}
                <div className={`p-3 rounded-xl ${stat.iconColor} bg-white/50  backdrop-blur-sm group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className="h-6 w-6" strokeWidth={2.5} />
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Status Distribution Pie Chart */}
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

          {/* Status Overview Bar Chart */}
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

        {/* Recent Investigations Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.4 }}
          className="bg-card border-0 rounded-2xl shadow-premium overflow-hidden"
        >
          <div className="p-6 border-b border-slate-100  flex items-center justify-between">
            <h2 className="text-lg font-heading font-semibold text-foreground">
              Recent Investigations
            </h2>
            <button
              onClick={() => navigate('/investigations')}
              className="flex items-center gap-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors group"
            >
              View All
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 ">
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
              <tbody className="divide-y divide-slate-100 divide-slate-800">
                {recentCases.map((investigation, index) => (
                  <motion.tr
                    key={investigation.investigation_id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.9 + index * 0.05 }}
                    className="hover:bg-slate-50 hover:bg-slate-800/50 transition-colors"
                  >
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
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(investigation.status)}`}>
                        {investigation.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {new Date(investigation.assigned_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button
                        onClick={() => navigate(`/investigations/${investigation.investigation_id}`)}
                        className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                      >
                        View
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
};

export default Dashboard;
