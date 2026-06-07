import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Toaster } from 'sonner';
import ProtectedRoute from './components/ProtectedRoute';
import RoleBasedRedirect from './components/RoleBasedRedirect';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Workbench from './pages/Workbench';
import InvestigatorDashboard from './pages/InvestigatorDashboard';
import InvestigationList from './pages/InvestigationList';
import InvestigationDetail from './pages/InvestigationDetail';
import UsersManagement from './pages/admin/UsersManagement';
import CategoriesManagement from './pages/admin/CategoriesManagement';
import '@/App.css';

const App = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Toaster position="top-right" richColors />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute allowedRoles={['admin', 'assessor']}>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/workbench"
              element={
                <ProtectedRoute allowedRoles={['investigator']}>
                  <Workbench />
                </ProtectedRoute>
              }
            />
            <Route
              path="/investigator/dashboard"
              element={
                <ProtectedRoute allowedRoles={['investigator']}>
                  <InvestigatorDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/investigations"
              element={
                <ProtectedRoute>
                  <InvestigationList />
                </ProtectedRoute>
              }
            />
            <Route
              path="/investigations/:investigationId"
              element={
                <ProtectedRoute>
                  <InvestigationDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <UsersManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/categories"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <CategoriesManagement />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<RoleBasedRedirect />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
