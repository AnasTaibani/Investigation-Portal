import React, { useEffect, useState } from 'react';
import Layout from '../../components/Layout';
import { getCategories, getSubcategories, createCategory, createSubcategory, deleteCategory, deleteSubcategory, getServiceCategories, createServiceCategory, deleteServiceCategory } from '../../lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const CategoriesManagement = () => {
  const [categories, setCategories] = useState([]);
  const [subcategories, setSubcategories] = useState([]);
  const [serviceCategories, setServiceCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCategoryForm, setShowCategoryForm] = useState(false);
  const [showSubcategoryForm, setShowSubcategoryForm] = useState(false);
  const [showServiceCategoryForm, setShowServiceCategoryForm] = useState(false);

  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [subcategoryForm, setSubcategoryForm] = useState({ category_id: '', name: '', description: '' });
  const [serviceCategoryForm, setServiceCategoryForm] = useState({ name: '', description: '', requires_geo_tag: false });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [catRes, subRes, svcRes] = await Promise.all([
        getCategories(),
        getSubcategories(),
        getServiceCategories(),
      ]);
      setCategories(catRes.data);
      setSubcategories(subRes.data);
      setServiceCategories(svcRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCategory = async () => {
    try {
      await createCategory(categoryForm);
      toast.success('Category created');
      setCategoryForm({ name: '', description: '' });
      setShowCategoryForm(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create category');
    }
  };

  const handleCreateSubcategory = async () => {
    try {
      await createSubcategory(subcategoryForm);
      toast.success('Subcategory created');
      setSubcategoryForm({ category_id: '', name: '', description: '' });
      setShowSubcategoryForm(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create subcategory');
    }
  };

  const handleCreateServiceCategory = async () => {
    try {
      await createServiceCategory(serviceCategoryForm);
      toast.success('Service category created');
      setServiceCategoryForm({ name: '', description: '', requires_geo_tag: false });
      setShowServiceCategoryForm(false);
      loadData();
    } catch (error) {
      toast.error('Failed to create service category');
    }
  };

  const handleDeleteCategory = async (id) => {
    if (!window.confirm('Delete this category?')) return;
    try {
      await deleteCategory(id);
      toast.success('Category deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete category');
    }
  };

  const handleDeleteSubcategory = async (id) => {
    if (!window.confirm('Delete this subcategory?')) return;
    try {
      await deleteSubcategory(id);
      toast.success('Subcategory deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete subcategory');
    }
  };

  const handleDeleteServiceCategory = async (id) => {
    if (!window.confirm('Delete this service category?')) return;
    try {
      await deleteServiceCategory(id);
      toast.success('Service category deleted');
      loadData();
    } catch (error) {
      toast.error('Failed to delete service category');
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="categories-management-page">
        <div>
          <h1 className="text-[24px] font-semibold text-slate-900 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            Categories Management
          </h1>
          <p className="mt-1 text-[14px] text-slate-600">Manage investigation categories, subcategories, and service types</p>
        </div>

        <Tabs defaultValue="categories">
          <TabsList>
            <TabsTrigger value="categories">Categories</TabsTrigger>
            <TabsTrigger value="subcategories">Subcategories</TabsTrigger>
            <TabsTrigger value="services">Service Categories</TabsTrigger>
          </TabsList>

          <TabsContent value="categories" className="space-y-4">
            <div className="flex justify-end">
              <Dialog open={showCategoryForm} onOpenChange={setShowCategoryForm}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-700 text-white hover:bg-blue-800" data-testid="create-category-button">
                    <Plus className="h-4 w-4 mr-2" />
                    New Category
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Category</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label>Name</Label>
                      <Input value={categoryForm.name} onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })} data-testid="category-name-input" />
                    </div>
                    <div>
                      <Label>Description</Label>
                      <Textarea value={categoryForm.description} onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })} data-testid="category-description-input" />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setShowCategoryForm(false)}>Cancel</Button>
                      <Button onClick={handleCreateCategory} data-testid="create-category-submit-button">Create</Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="bg-white border border-slate-200 rounded-md shadow-sm">
              <table className="w-full text-left text-[13px]" data-testid="categories-table">
                <thead className="bg-slate-50 text-slate-700 font-medium">
                  <tr>
                    <th className="py-3 px-6 border-b border-slate-200">Name</th>
                    <th className="py-3 px-6 border-b border-slate-200">Description</th>
                    <th className="py-3 px-6 border-b border-slate-200">Actions</th>
                  </tr>
                </thead>
                <tbody className="text-slate-600">
                  {categories.map((cat) => (
                    <tr key={cat.id} className="hover:bg-slate-50">
                      <td className="py-3 px-6 border-b border-slate-100 text-slate-900 font-medium">{cat.name}</td>
                      <td className="py-3 px-6 border-b border-slate-100">{cat.description || '-'}</td>
                      <td className="py-3 px-6 border-b border-slate-100">
                        <button onClick={() => handleDeleteCategory(cat.id)} className="text-red-600 hover:text-red-700" data-testid={`delete-category-${cat.id}`}>
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabsContent>

          <TabsContent value="subcategories" className="space-y-4">
            <div className="flex justify-end">
              <Dialog open={showSubcategoryForm} onOpenChange={setShowSubcategoryForm}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-700 text-white hover:bg-blue-800" data-testid="create-subcategory-button">
                    <Plus className="h-4 w-4 mr-2" />
                    New Subcategory
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Subcategory</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label>Category</Label>
                      <select
                        className="w-full border border-slate-300 rounded-md p-2 text-[14px]"
                        value={subcategoryForm.category_id}
                        onChange={(e) => setSubcategoryForm({ ...subcategoryForm, category_id: e.target.value })}
                        data-testid="subcategory-category-select"
                      >
                        <option value="">Select Category</option>
                        {categories.map((cat) => (
                          <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label>Name</Label>
                      <Input value={subcategoryForm.name} onChange={(e) => setSubcategoryForm({ ...subcategoryForm, name: e.target.value })} data-testid="subcategory-name-input" />
                    </div>
                    <div>
                      <Label>Description</Label>
                      <Textarea value={subcategoryForm.description} onChange={(e) => setSubcategoryForm({ ...subcategoryForm, description: e.target.value })} data-testid="subcategory-description-input" />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setShowSubcategoryForm(false)}>Cancel</Button>
                      <Button onClick={handleCreateSubcategory} data-testid="create-subcategory-submit-button">Create</Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="bg-white border border-slate-200 rounded-md shadow-sm">
              <table className="w-full text-left text-[13px]" data-testid="subcategories-table">
                <thead className="bg-slate-50 text-slate-700 font-medium">
                  <tr>
                    <th className="py-3 px-6 border-b border-slate-200">Category</th>
                    <th className="py-3 px-6 border-b border-slate-200">Name</th>
                    <th className="py-3 px-6 border-b border-slate-200">Description</th>
                    <th className="py-3 px-6 border-b border-slate-200">Actions</th>
                  </tr>
                </thead>
                <tbody className="text-slate-600">
                  {subcategories.map((sub) => {
                    const category = categories.find((c) => c.id === sub.category_id);
                    return (
                      <tr key={sub.id} className="hover:bg-slate-50">
                        <td className="py-3 px-6 border-b border-slate-100">{category?.name || '-'}</td>
                        <td className="py-3 px-6 border-b border-slate-100 text-slate-900 font-medium">{sub.name}</td>
                        <td className="py-3 px-6 border-b border-slate-100">{sub.description || '-'}</td>
                        <td className="py-3 px-6 border-b border-slate-100">
                          <button onClick={() => handleDeleteSubcategory(sub.id)} className="text-red-600 hover:text-red-700" data-testid={`delete-subcategory-${sub.id}`}>
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </TabsContent>

          <TabsContent value="services" className="space-y-4">
            <div className="flex justify-end">
              <Dialog open={showServiceCategoryForm} onOpenChange={setShowServiceCategoryForm}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-700 text-white hover:bg-blue-800" data-testid="create-service-category-button">
                    <Plus className="h-4 w-4 mr-2" />
                    New Service Category
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Service Category</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label>Name</Label>
                      <Input value={serviceCategoryForm.name} onChange={(e) => setServiceCategoryForm({ ...serviceCategoryForm, name: e.target.value })} data-testid="service-category-name-input" />
                    </div>
                    <div>
                      <Label>Description</Label>
                      <Textarea value={serviceCategoryForm.description} onChange={(e) => setServiceCategoryForm({ ...serviceCategoryForm, description: e.target.value })} data-testid="service-category-description-input" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        id="requires_geo_tag"
                        checked={serviceCategoryForm.requires_geo_tag}
                        onCheckedChange={(checked) => setServiceCategoryForm({ ...serviceCategoryForm, requires_geo_tag: checked })}
                        data-testid="service-category-geotag-checkbox"
                      />
                      <Label htmlFor="requires_geo_tag" className="text-[13px] cursor-pointer">Requires Geo-Tagging</Label>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setShowServiceCategoryForm(false)}>Cancel</Button>
                      <Button onClick={handleCreateServiceCategory} data-testid="create-service-category-submit-button">Create</Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="bg-white border border-slate-200 rounded-md shadow-sm">
              <table className="w-full text-left text-[13px]" data-testid="service-categories-table">
                <thead className="bg-slate-50 text-slate-700 font-medium">
                  <tr>
                    <th className="py-3 px-6 border-b border-slate-200">Name</th>
                    <th className="py-3 px-6 border-b border-slate-200">Description</th>
                    <th className="py-3 px-6 border-b border-slate-200">Geo-Tag Required</th>
                    <th className="py-3 px-6 border-b border-slate-200">Actions</th>
                  </tr>
                </thead>
                <tbody className="text-slate-600">
                  {serviceCategories.map((svc) => (
                    <tr key={svc.id} className="hover:bg-slate-50">
                      <td className="py-3 px-6 border-b border-slate-100 text-slate-900 font-medium">{svc.name}</td>
                      <td className="py-3 px-6 border-b border-slate-100">{svc.description || '-'}</td>
                      <td className="py-3 px-6 border-b border-slate-100">
                        {svc.requires_geo_tag ? <span className="text-green-600">Yes</span> : <span className="text-slate-400">No</span>}
                      </td>
                      <td className="py-3 px-6 border-b border-slate-100">
                        <button onClick={() => handleDeleteServiceCategory(svc.id)} className="text-red-600 hover:text-red-700" data-testid={`delete-service-category-${svc.id}`}>
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default CategoriesManagement;
