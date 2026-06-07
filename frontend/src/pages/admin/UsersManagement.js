import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { getUsers, deleteUser } from '../../lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2, Edit, Search } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../lib/api';

const UsersManagement = () => {
  const { register } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    role: 'investigator',
    phone: '',
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const { data } = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error('Error loading users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const result = await register(form);
      if (result.success) {
        toast.success('User created successfully');
        setShowCreateForm(false);
        setForm({ email: '', password: '', name: '', role: 'investigator', phone: '' });
        loadUsers();
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to create user');
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await deleteUser(userId);
      toast.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      toast.error('Failed to delete user');
    }
  };

  const filteredUsers = users.filter((u) =>
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="space-y-6" data-testid="users-management-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-[24px] font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
              Users Management
            </h1>
            <p className="mt-1 text-[14px] text-slate-600">Manage investigators, assessors, and administrators</p>
          </div>
          <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
            <DialogTrigger asChild>
              <Button className="bg-blue-700 text-white hover:bg-blue-800" data-testid="create-user-button">
                <Plus className="h-4 w-4 mr-2" />
                New User
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Name</Label>
                  <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="user-name-input" />
                </div>
                <div>
                  <Label>Email</Label>
                  <Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} data-testid="user-email-input" />
                </div>
                <div>
                  <Label>Password</Label>
                  <Input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} data-testid="user-password-input" />
                </div>
                <div>
                  <Label>Phone</Label>
                  <Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} data-testid="user-phone-input" />
                </div>
                <div>
                  <Label>Role</Label>
                  <Select value={form.role} onValueChange={(value) => setForm({ ...form, role: value })}>
                    <SelectTrigger data-testid="user-role-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="investigator">Investigator</SelectItem>
                      <SelectItem value="assessor">Assessor</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setShowCreateForm(false)}>Cancel</Button>
                  <Button onClick={handleCreate} data-testid="create-user-submit-button">Create User</Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="bg-white border border-slate-200 rounded-md shadow-sm p-6">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
                placeholder="Search users..."
                data-testid="search-users-input"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-[13px]" data-testid="users-table">
              <thead className="bg-slate-50 text-slate-700 font-medium">
                <tr>
                  <th className="py-3 px-6 border-b border-slate-200">Name</th>
                  <th className="py-3 px-6 border-b border-slate-200">Email</th>
                  <th className="py-3 px-6 border-b border-slate-200">Phone</th>
                  <th className="py-3 px-6 border-b border-slate-200">Role</th>
                  <th className="py-3 px-6 border-b border-slate-200">Created</th>
                  <th className="py-3 px-6 border-b border-slate-200">Actions</th>
                </tr>
              </thead>
              <tbody className="text-slate-600">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50">
                    <td className="py-3 px-6 border-b border-slate-100 text-slate-900 font-medium">{user.name}</td>
                    <td className="py-3 px-6 border-b border-slate-100">{user.email}</td>
                    <td className="py-3 px-6 border-b border-slate-100">{user.phone || '-'}</td>
                    <td className="py-3 px-6 border-b border-slate-100">
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-800 rounded-full text-xs font-medium capitalize">
                        {user.role}
                      </span>
                    </td>
                    <td className="py-3 px-6 border-b border-slate-100">{new Date(user.created_at).toLocaleDateString()}</td>
                    <td className="py-3 px-6 border-b border-slate-100">
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="text-red-600 hover:text-red-700"
                        data-testid={`delete-user-${user.id}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default UsersManagement;
