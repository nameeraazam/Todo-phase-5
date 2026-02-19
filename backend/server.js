import express from 'express';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';

const app = express();
const PORT = 8000;
const JWT_SECRET = 'your-secret-key-change-in-production';

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage (in a real app, this would be a database)
let users = [];
let tasks = [];

// Helper function to generate timestamps
const generateTimestamp = () => new Date().toISOString();

// Authentication Middleware
const authenticate = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];

  try {
    // Verify JWT token
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ message: 'Invalid token' });
  }
};

// Root route to fix "Cannot GET /"
app.get('/', (req, res) => {
  res.send('Backend is running 🚀');
});

// Auth routes
app.post('/api/auth/signup', async (req, res) => {
  console.log('Signup request received:', req.body);
  const { email, name } = req.body;

  if (!email) {
    return res.status(400).json({ message: 'Email is required' });
  }

  // Auto-signup/login logic
  let user = users.find(u => u.email === email);
  if (!user) {
    user = {
      id: uuidv4(),
      email,
      name: name || email.split('@')[0],
      createdAt: generateTimestamp(),
      updatedAt: generateTimestamp()
    };
    users.push(user);
  }

  const token = jwt.sign(
    { id: user.id, email: user.email, name: user.name },
    JWT_SECRET,
    { expiresIn: '24h' }
  );

  res.json({ user, token });
});

app.post('/api/auth/signin', async (req, res) => {
  console.log('Signin request received:', req.body);
  const { email, name } = req.body;

  if (!email) {
    return res.status(400).json({ message: 'Email is required' });
  }

  // Find user by email or create new one
  let user = users.find(user => user.email === email);
  
  if (!user) {
    user = {
      id: uuidv4(),
      email,
      name: name || email.split('@')[0],
      createdAt: generateTimestamp(),
      updatedAt: generateTimestamp()
    };
    users.push(user);
  }

  // Create JWT token
  const token = jwt.sign(
    { id: user.id, email: user.email, name: user.name },
    JWT_SECRET,
    { expiresIn: '24h' }
  );

  res.json({ user, token });
});

app.post('/api/auth/signout', (req, res) => {
  // In a real app, you would invalidate the token here
  // For this mock, we'll just return success
  res.json({ message: 'Signed out successfully' });
});

app.get('/api/auth/me', authenticate, (req, res) => {
  res.json(req.user);
});

// Task routes (Protected)
app.get('/api/tasks', authenticate, (req, res) => {
  // Return only tasks belonging to the authenticated user, sorted by completion and date
  const userTasks = tasks
    .filter(task => task.userId === req.user.id)
    .sort((a, b) => {
      if (a.completed !== b.completed) {
        return a.completed ? 1 : -1;
      }
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });
  res.json(userTasks);
});

app.post('/api/tasks', authenticate, (req, res) => {
  const { title, description } = req.body;

  // Validate input
  if (!title || title.trim() === '') {
    return res.status(400).json({ message: 'Title is required' });
  }

  // Create new task
  const newTask = {
    id: uuidv4(),
    userId: req.user.id,
    title: title.trim(),
    description: description ? description.trim() : undefined,
    completed: false,
    createdAt: generateTimestamp(),
    updatedAt: generateTimestamp(),
    completedAt: null
  };

  tasks.push(newTask);

  res.status(201).json(newTask);
});

app.put('/api/tasks/:id', authenticate, (req, res) => {
  const taskId = req.params.id;
  const { title, description, completed } = req.body;

  // Find the task
  const taskIndex = tasks.findIndex(task => task.id === taskId && task.userId === req.user.id);
  if (taskIndex === -1) {
    return res.status(404).json({ message: 'Task not found' });
  }

  // Update the task
  const updatedTask = {
    ...tasks[taskIndex],
    ...(title !== undefined && { title: title.trim() }),
    ...(description !== undefined && { description: description.trim() }),
    ...(completed !== undefined && { 
      completed,
      completedAt: completed ? generateTimestamp() : null
    }),
    updatedAt: generateTimestamp()
  };

  tasks[taskIndex] = updatedTask;

  res.json(updatedTask);
});

app.delete('/api/tasks/:id', authenticate, (req, res) => {
  const taskId = req.params.id;

  // Find the task
  const taskIndex = tasks.findIndex(task => task.id === taskId && task.userId === req.user.id);
  if (taskIndex === -1) {
    return res.status(404).json({ message: 'Task not found' });
  }

  // Remove the task
  tasks.splice(taskIndex, 1);

  res.json({ message: 'Task deleted successfully' });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: generateTimestamp() });
});

// Start server
if (process.env.NODE_ENV !== 'production') {
  app.listen(PORT, () => {
    console.log(`Mock API server is running on http://localhost:${PORT}`);
  });
}

export default app;
