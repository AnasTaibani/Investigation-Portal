import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import BrandLogo from './BrandLogo';
import {
  LayoutDashboard,
  FolderSearch,
  Users,
  Building2,
  FolderTree,
  Bell,
  LogOut,
  Menu,
  X,
  Search,
  ChevronRight,
  ChevronLeft,
  Briefcase,
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navigation = user?.role === 'investigator' 
    ? [
        { name: 'Workbench', href: '/workbench', icon: Briefcase, roles: ['investigator'] },
        { name: 'Investigation Enquiry', href: '/investigations', icon: FolderSearch, roles: ['investigator'] },
        { name: 'Dashboard', href: '/investigator/dashboard', icon: LayoutDashboard, roles: ['investigator'] },
      ]
    : [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['assessor', 'admin'] },
        { name: 'Investigations', href: '/investigations', icon: FolderSearch, roles: ['assessor', 'admin'] },
        { name: 'Users', href: '/users', icon: Users, roles: ['admin'] },
        { name: 'Agencies', href: '/agencies', icon: Building2, roles: ['admin'] },
        { name: 'Categories', href: '/categories', icon: FolderTree, roles: ['admin'] },
      ];

  const filteredNavigation = navigation.filter((item) => item.roles.includes(user?.role));

  // Generate breadcrumbs from current path
  const getBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    return paths.map((path, index) => {
      const href = '/' + paths.slice(0, index + 1).join('/');
      const label = path.charAt(0).toUpperCase() + path.slice(1);
      return { label, href };
    });
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <div className="min-h-screen bg-background transition-colors">
      {/* Premium Header with Glassmorphism */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-slate-200/50 transition-premium"
      >
        <div className="px-6 py-3 flex items-center justify-between gap-4">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            {/* Desktop Sidebar Toggle */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hidden lg:flex p-2 hover:bg-slate-100 rounded-lg transition-premium"
              data-testid="sidebar-toggle-btn"
            >
              {sidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-premium"
              data-testid="mobile-menu-toggle"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            {/* Breadcrumbs - Hidden on mobile */}
            <nav className="hidden md:flex items-center gap-2 text-sm">
              <Link 
                to="/dashboard"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Home
              </Link>
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={crumb.href}>
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  <Link
                    to={crumb.href}
                    className={`${
                      index === breadcrumbs.length - 1
                        ? 'text-foreground font-medium'
                        : 'text-muted-foreground hover:text-foreground'
                    } transition-colors`}
                  >
                    {crumb.label}
                  </Link>
                </React.Fragment>
              ))}
            </nav>
          </div>

          {/* Center Section - Global Search */}
          <div className="hidden lg:flex flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search investigations... (⌘K)"
                className="w-full pl-10 pr-4 py-2 bg-slate-100 border-0 rounded-lg text-sm focus:ring-2 focus:ring-primary transition-all"
                data-testid="global-search-input"
              />
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            <button
              className="p-2 hover:bg-slate-100 rounded-lg transition-premium relative"
              data-testid="notifications-button"
              onClick={() => navigate('/notifications')}
            >
              <Bell className="h-5 w-5" />
              {/* Notification badge */}
              <span className="absolute top-1 right-1 h-2 w-2 bg-brand-secondary rounded-full"></span>
            </button>

            {/* User Profile */}
            <div className="hidden md:flex items-center gap-3 pl-3 border-l border-slate-200 dark:border-slate-800">
              <div className="text-right">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
              </div>
              <Button
                onClick={handleLogout}
                variant="ghost"
                size="sm"
                className="hover:bg-slate-100"
                data-testid="logout-button"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="flex">
        {/* Premium Collapsible Sidebar - Desktop */}
        <motion.aside
          initial={false}
          animate={{ width: sidebarOpen ? 240 : 72 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="hidden lg:block fixed left-0 top-0 h-screen bg-card border-r border-border z-40 pt-20"
          data-testid="sidebar"
        >
          {/* Logo in Sidebar */}
          <div className="px-4 pb-4 border-b border-border">
            <AnimatePresence mode="wait">
              {sidebarOpen ? (
                <motion.div
                  key="expanded"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <BrandLogo size="md" />
                </motion.div>
              ) : (
                <motion.div
                  key="collapsed"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex justify-center"
                >
                  <BrandLogo variant="icon" size="sm" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Navigation */}
          <nav className="p-3 space-y-1 custom-scrollbar overflow-y-auto h-[calc(100vh-180px)]">
            {filteredNavigation.map((item) => {
              const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/');
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all relative ${
                    isActive
                      ? 'bg-blue-50 text-brand-primary shadow-soft'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                  data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
                >
                  {/* Active indicator bar */}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-brand-primary rounded-r-full"
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}
                  
                  <item.icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-brand-primary' : 'text-slate-500 group-hover:text-slate-900 group-hover:scale-110 transition-transform'}`} />
                  
                  <AnimatePresence>
                    {sidebarOpen && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: 'auto' }}
                        exit={{ opacity: 0, width: 0 }}
                        transition={{ duration: 0.2 }}
                        className="whitespace-nowrap overflow-hidden"
                      >
                        {item.name}
                      </motion.span>
                    )}
                  </AnimatePresence>
                </Link>
              );
            })}
          </nav>
        </motion.aside>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="lg:hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40"
                onClick={() => setMobileMenuOpen(false)}
              />
              <motion.aside
                initial={{ x: -300 }}
                animate={{ x: 0 }}
                exit={{ x: -300 }}
                transition={{ type: 'spring', damping: 25 }}
                className="lg:hidden fixed left-0 top-0 bottom-0 w-64 bg-card border-r border-border z-50 pt-20"
              >
                <div className="px-4 pb-4 border-b border-border">
                  <BrandLogo size="md" />
                </div>
                <nav className="p-3 space-y-1">
                  {filteredNavigation.map((item) => {
                    const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/');
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                          isActive
                            ? 'bg-blue-50/50 text-brand-primary'
                            : 'text-muted-foreground hover:text-foreground hover:bg-slate-100'
                        }`}
                      >
                        <item.icon className="h-5 w-5" />
                        {item.name}
                      </Link>
                    );
                  })}
                </nav>
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content Area */}
        <motion.main
          animate={{ marginLeft: sidebarOpen ? 240 : 72 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="flex-1 p-6 lg:p-8 min-h-[calc(100vh-64px)] mt-16"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
          >
            {children}
          </motion.div>
        </motion.main>
      </div>
    </div>
  );
};

export default Layout;
