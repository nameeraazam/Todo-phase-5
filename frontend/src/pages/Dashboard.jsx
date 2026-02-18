import { useState, useEffect } from 'react';
import { Plus, Trash2, Edit2, Check, X, Search, Filter, Calendar, Clock } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = 'http://localhost:8000';

export default function Dashboard({ user, token }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [editingTask, setEditingTask] = useState(null);
  const [editForm, setEditForm] = useState({ title: '', description: '', completed: false });
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/tasks`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    try {
      const response = await axios.post(`${API_URL}/api/tasks`, newTask, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTasks([response.data, ...tasks]);
      setNewTask({ title: '', description: '' });
      toast.success('Task created successfully!');
    } catch (error) {
      console.error('Error creating task:', error);
      toast.error('Failed to create task');
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      const response = await axios.put(`${API_URL}/api/tasks/${taskId}`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTasks(tasks.map(task => task.id === taskId ? response.data : task));
      toast.success('Task updated!');
    } catch (error) {
      console.error('Error updating task:', error);
      toast.error('Failed to update task');
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await axios.delete(`${API_URL}/api/tasks/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setTasks(tasks.filter(task => task.id !== taskId));
      toast.success('Task deleted');
    } catch (error) {
      console.error('Error deleting task:', error);
      toast.error('Failed to delete task');
    }
  };

  const toggleComplete = async (task) => {
    await updateTask(task.id, { completed: !task.completed });
  };

  const startEditing = (task) => {
    setEditingTask(task.id);
    setEditForm({
      title: task.title,
      description: task.description || '',
      completed: task.completed
    });
  };

  const cancelEditing = () => {
    setEditingTask(null);
    setEditForm({ title: '', description: '', completed: false });
  };

  const saveEdit = async (taskId) => {
    await updateTask(taskId, editForm);
    cancelEditing();
  };

  const filteredTasks = tasks.filter(task => {
    const matchesFilter = 
      filter === 'all' ? true :
      filter === 'active' ? !task.completed :
      task.completed;
    
    const matchesSearch = 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesFilter && matchesSearch;
  });

  const stats = {
    total: tasks.length,
    active: tasks.filter(t => !t.completed).length,
    completed: tasks.filter(t => t.completed).length
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Hello, {user?.name || user?.email}! 👋
        </h1>
        <p className="text-gray-600">Manage your tasks efficiently</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Total Tasks</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <Filter className="h-12 w-12 text-blue-200" />
          </div>
        </div>
        
        <div className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Active</p>
              <p className="text-3xl font-bold">{stats.active}</p>
            </div>
            <Clock className="h-12 w-12 text-orange-200" />
          </div>
        </div>
        
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Completed</p>
              <p className="text-3xl font-bold">{stats.completed}</p>
            </div>
            <Check className="h-12 w-12 text-green-200" />
          </div>
        </div>
      </div>

      {/* Create Task Form */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
        <form onSubmit={createTask} className="space-y-4">
          <div>
            <input
              type="text"
              value={newTask.title}
              onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              placeholder="Task title..."
              className="input-field"
            />
          </div>
          <div>
            <textarea
              value={newTask.description}
              onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              placeholder="Task description (optional)..."
              rows="3"
              className="input-field resize-none"
            />
          </div>
          <button type="submit" className="btn-primary flex items-center space-x-2">
            <Plus className="h-5 w-5" />
            <span>Add Task</span>
          </button>
        </form>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search tasks..."
            className="input-field pl-10"
          />
        </div>
        
        <div className="flex gap-2">
          {['all', 'active', 'completed'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === f
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tasks List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="card text-center py-12">
            <div className="text-gray-400 mb-4">
              <Calendar className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {searchQuery || filter !== 'all' ? 'No tasks found' : 'No tasks yet'}
            </h3>
            <p className="text-gray-600">
              {searchQuery || filter !== 'all' 
                ? 'Try adjusting your search or filter' 
                : 'Create your first task above!'}
            </p>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`card transition-all duration-200 ${
                task.completed ? 'opacity-75 bg-gray-50' : 'hover:shadow-xl'
              }`}
            >
              {editingTask === task.id ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    className="input-field"
                  />
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    className="input-field resize-none"
                    rows="2"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => saveEdit(task.id)}
                      className="btn-primary flex items-center space-x-1 py-1 px-3 text-sm"
                    >
                      <Check className="h-4 w-4" />
                      <span>Save</span>
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="btn-secondary flex items-center space-x-1 py-1 px-3 text-sm"
                    >
                      <X className="h-4 w-4" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-4">
                  <button
                    onClick={() => toggleComplete(task)}
                    className={`mt-1 flex-shrink-0 h-6 w-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                      task.completed
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'border-gray-300 hover:border-primary-500'
                    }`}
                  >
                    {task.completed && <Check className="h-4 w-4" />}
                  </button>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className={`text-lg font-semibold ${
                      task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                    }`}>
                      {task.title}
                    </h3>
                    {task.description && (
                      <p className={`mt-1 ${
                        task.completed ? 'text-gray-400' : 'text-gray-600'
                      }`}>
                        {task.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(task.createdAt).toLocaleDateString()}
                      </span>
                      {task.completedAt && (
                        <span className="flex items-center gap-1 text-green-600">
                          <Check className="h-4 w-4" />
                          Completed {new Date(task.completedAt).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => startEditing(task)}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                    >
                      <Edit2 className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => deleteTask(task.id)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
