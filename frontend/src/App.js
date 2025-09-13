import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";
import { Badge } from "./components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { toast } from "sonner";
import { Toaster } from "./components/ui/sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Activity, Users, Bot, Shield, Play, Clock, CheckCircle, XCircle, Settings } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Mock SaaS Portal Component
const MockSaaSPortal = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showMFA, setShowMFA] = useState(false);
  const [sessionToken, setSessionToken] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [otpCode, setOtpCode] = useState("");
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });
  const [filters, setFilters] = useState({ search: "", role: "", status: "" });
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUser, setNewUser] = useState({ name: "", email: "", role: "user" });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/mock-saas/login`, credentials);
      if (response.data.requires_mfa) {
        setSessionToken(response.data.session_token);
        setShowMFA(true);
        toast.success("Credentials verified. Please enter MFA code.");
      }
    } catch (error) {
      toast.error("Login failed. Try admin/password");
    }
    setLoading(false);
  };

  const handleMFA = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/mock-saas/verify-mfa`, {
        otp_code: otpCode,
        session_token: sessionToken
      });
      setAccessToken(response.data.access_token);
      setIsAuthenticated(true);
      setShowMFA(false);
      toast.success("Authentication successful!");
      fetchUsers();
    } catch (error) {
      toast.error("Invalid MFA code. Try any 6 digits (e.g., 123456)");
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString(),
        ...Object.fromEntries(Object.entries(filters).filter(([_, value]) => value))
      });
      
      const response = await axios.get(`${API}/mock-saas/users?${params}`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      
      setUsers(response.data.users);
      setPagination(prev => ({ ...prev, total: response.data.total, pages: response.data.pages }));
    } catch (error) {
      toast.error("Failed to fetch users");
    }
    setLoading(false);
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/mock-saas/users`, newUser, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      toast.success("User created successfully!");
      setShowAddUser(false);
      setNewUser({ name: "", email: "", role: "user" });
      fetchUsers();
    } catch (error) {
      toast.error("Failed to create user");
    }
  };

  const handleDeleteUser = async (userId) => {
    try {
      await axios.delete(`${API}/mock-saas/users/${userId}`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      toast.success("User deleted successfully!");
      fetchUsers();
    } catch (error) {
      toast.error("Failed to delete user");
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchUsers();
    }
  }, [pagination.page, filters, isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <CardTitle className="text-2xl">Mock SaaS Portal</CardTitle>
            <p className="text-gray-600">Enterprise User Management System</p>
          </CardHeader>
          <CardContent>
            {!showMFA ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="admin"
                    value={credentials.username}
                    onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="password"
                    value={credentials.password}
                    onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? "Authenticating..." : "Sign In"}
                </Button>
                <p className="text-sm text-gray-500 text-center">
                  Demo credentials: admin / password
                </p>
              </form>
            ) : (
              <form onSubmit={handleMFA} className="space-y-4">
                <div className="text-center mb-4">
                  <p className="text-sm text-gray-600">Enter the 6-digit code from your authenticator app</p>
                </div>
                <div>
                  <Label htmlFor="otp">MFA Code</Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="123456"
                    maxLength="6"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    required
                  />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? "Verifying..." : "Verify Code"}
                </Button>
                <p className="text-sm text-gray-500 text-center">
                  Demo: Use any 6 digits (e.g., 123456)
                </p>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'user': return 'bg-blue-100 text-blue-800';
      case 'viewer': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="border-b bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold">Enterprise Portal</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">Mock SaaS Environment</Badge>
              <Button variant="outline" size="sm" onClick={() => {
                setIsAuthenticated(false);
                setAccessToken("");
                toast.info("Logged out successfully");
              }}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-2">User Management</h2>
          <p className="text-gray-600">Manage users, roles, and access permissions</p>
        </div>

        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Input
              placeholder="Search users..."
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              className="w-64"
            />
            <Select value={filters.role || "all"} onValueChange={(value) => setFilters({...filters, role: value === "all" ? "" : value})}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="user">User</SelectItem>
                <SelectItem value="viewer">Viewer</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filters.status || "all"} onValueChange={(value) => setFilters({...filters, status: value === "all" ? "" : value})}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <Dialog open={showAddUser} onOpenChange={setShowAddUser}>
            <DialogTrigger asChild>
              <Button>Add User</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New User</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleAddUser} className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    value={newUser.name}
                    onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newUser.email}
                    onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Select value={newUser.role} onValueChange={(value) => setNewUser({...newUser, role: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="user">User</SelectItem>
                      <SelectItem value="viewer">Viewer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setShowAddUser(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">Create User</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardContent className="p-0">
            <Table id="users">
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge className={getRoleColor(user.role)} variant="secondary">
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(user.status)} variant="secondary">
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.last_login || "Never"}</TableCell>
                    <TableCell>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        Remove
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {pagination.pages > 1 && (
          <div className="flex justify-center mt-6">
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {pagination.page} of {pagination.pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page === pagination.pages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Automation Control Dashboard
const AutomationDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/automation/jobs`);
      setJobs(response.data);
    } catch (error) {
      toast.error("Failed to fetch automation jobs");
    }
  };

  const createJob = async (jobType, parameters = {}) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/automation/jobs`, null, {
        params: { job_type: jobType, parameters: JSON.stringify(parameters) }
      });
      toast.success(`${jobType} job created successfully!`);
      fetchJobs();
    } catch (error) {
      toast.error("Failed to create automation job");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-600" />;
      case 'running': return <Activity className="w-4 h-4 text-blue-600 animate-spin" />;
      default: return <Clock className="w-4 h-4 text-yellow-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'running': return 'bg-blue-100 text-blue-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <Button
              onClick={() => createJob('scrape_users')}
              disabled={loading}
              className="w-full h-20 flex flex-col items-center justify-center space-y-2"
            >
              <Users className="w-6 h-6" />
              <span>Scrape Users</span>
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <Button
              onClick={() => createJob('provision_user', { name: 'Test User', email: 'test@example.com', role: 'user' })}
              disabled={loading}
              className="w-full h-20 flex flex-col items-center justify-center space-y-2"
              variant="outline"
            >
              <Bot className="w-6 h-6" />
              <span>Provision User</span>
            </Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <Button
              onClick={() => createJob('deprovision_user', { user_id: 'demo-user-1' })}
              disabled={loading}
              className="w-full h-20 flex flex-col items-center justify-center space-y-2"
              variant="secondary"
            >
              <Settings className="w-6 h-6" />
              <span>Deprovision User</span>
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Automation Jobs</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Job Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium">{job.job_type}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(job.status)}
                        <Badge className={getStatusColor(job.status)} variant="secondary">
                          {job.status}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>{new Date(job.created_at).toLocaleString()}</TableCell>
                    <TableCell>
                      {job.completed_at 
                        ? `${Math.round((new Date(job.completed_at) - new Date(job.created_at)) / 1000)}s`
                        : '-'
                      }
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedJob(job)}
                      >
                        View Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {selectedJob && (
        <Dialog open={!!selectedJob} onOpenChange={() => setSelectedJob(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Job Details: {selectedJob.job_type}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Status</h4>
                <Badge className={getStatusColor(selectedJob.status)}>
                  {selectedJob.status}
                </Badge>
              </div>
              
              {selectedJob.logs && selectedJob.logs.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Execution Logs</h4>
                  <div className="bg-gray-50 rounded p-3 space-y-1 max-h-40 overflow-y-auto">
                    {selectedJob.logs.map((log, index) => (
                      <div key={index} className="text-sm font-mono">{log}</div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedJob.results && Object.keys(selectedJob.results).length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Results</h4>
                  <pre className="bg-gray-50 rounded p-3 text-sm overflow-x-auto">
                    {JSON.stringify(selectedJob.results, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <div className="App">
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50">
          <nav className="bg-white border-b">
            <div className="container mx-auto px-4">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center space-x-8">
                  <Link to="/" className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-semibold text-lg">AI Web Automation</span>
                  </Link>
                  <div className="flex space-x-6">
                    <Link 
                      to="/mock-saas" 
                      className="text-gray-600 hover:text-gray-900 flex items-center space-x-1"
                    >
                      <Shield className="w-4 h-4" />
                      <span>Mock SaaS Portal</span>
                    </Link>
                    <Link 
                      to="/automation" 
                      className="text-gray-600 hover:text-gray-900 flex items-center space-x-1"
                    >
                      <Settings className="w-4 h-4" />
                      <span>Automation Control</span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/mock-saas" element={<MockSaaSPortal />} />
            <Route path="/automation" element={<AutomationDashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
      <Toaster />
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">AI-Driven Web Automation Demo</h1>
        <p className="text-gray-600 text-lg">
          Demonstrating automated SaaS user management using AI, RPA, and headless browsers
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Mock SaaS Portal</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              A simulated enterprise SaaS application with user management features, MFA, and role-based access.
            </p>
            <Link to="/mock-saas">
              <Button className="w-full">
                Access Mock Portal
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="w-5 h-5" />
              <span>Automation Control</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Control center for managing automation jobs, monitoring progress, and viewing results.
            </p>
            <Link to="/automation">
              <Button variant="outline" className="w-full">
                Open Control Center
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Architecture</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Users className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <h3 className="font-medium">Mock SaaS Portal</h3>
                <p className="text-sm text-gray-600">Target system with authentication, user management, and varying UI elements</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Bot className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <h3 className="font-medium">AI Automation Engine</h3>
                <p className="text-sm text-gray-600">Playwright-based automation with simulated AI for DOM parsing and adaptation</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Activity className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <h3 className="font-medium">Control Dashboard</h3>
                <p className="text-sm text-gray-600">Job management, monitoring, and results visualization</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default App;