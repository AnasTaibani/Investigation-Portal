import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { getDashboardStats } from '../lib/api';
import {
  FolderOpen,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  TrendingUp,
  TrendingDown,
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

const InvestigatorDashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await getDashboardStats();
      setStats(statsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const statsCards = [
    { label: 'Assigned', value: stats?.assigned || 0, icon: FolderOpen, bgLight: 'bg-blue-50/50', iconColor: 'text-blue-600', trend: '+12%', trendUp: true },
    { label: 'In Progress', value: stats?.in_progress || 0, icon: Clock, bgLight: 'bg-amber-50/50', iconColor: 'text-amber-600', trend: '+8%', trendUp: true },
    { label: 'Submitted', value: stats?.submitted || 0, icon: FileCheck, bgLight: 'bg-emerald-50/50', iconColor: 'text-emerald-600', trend: '+16%', trendUp: true },
    { label: 'Rework Requested', value: stats?.rework_requested || 0, icon: AlertTriangle, bgLight: 'bg-red-50/50', iconColor: 'text-red-600', trend: '-5%', trendUp: false },
    { label: 'Completed', value: stats?.completed || 0, icon: CheckCircle2, bgLight: 'bg-green-50/50', iconColor: 'text-green-600', trend: '+20%', trendUp: true },
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
        data-testid="investigator-dashboard-page"
      >
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
            Track your investigation performance and metrics
          </p>
        </motion.div>

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
      </motion.div>
    </Layout>
  );
};

export default InvestigatorDashboard;
