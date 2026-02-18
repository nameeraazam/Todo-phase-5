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
  const { email, password, name } = req.body;

  // Check if user already exists
  const existingUser = users.find(user => user.email === email);
  if (existingUser) {
    return res.status(400).json({ message: 'User already exists' });
  }

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);

  // Create new user
  const newUser = {
    id: uuidv4(),
    email,
    name,
    password: hashedPassword,
    createdAt: generateTimestamp(),
    updatedAt: generateTimestamp()
  };

  users.push(newUser);

  // Create JWT token
  const token = jwt.sign(
    { id: newUser.id, email: newUser.email, name: newUser.name },
    JWT_SECRET,
    { expiresIn: '24h' }
  );

  // Return user data with token (don't send password)
  const { password: _, ...userWithoutPassword } = newUser;
  res.json({
    user: userWithoutPassword,
    token
  });
});

app.post('/api/auth/signin', async (req, res) => {
  const { email, password, name } = req.body;

  // Find user by email
  let user = users.find(user => user.email === email);
  
  // If user doesn't exist, create a new one (auto-signup)
  if (!user) {
    const hashedPassword = await bcrypt.hash(password || 'default', 10);
    user = {
      id: uuidv4(),
      email,
      name: name || email.split('@')[0],
      password: hashedPassword,
      createdAt: generateTimestamp(),
      updatedAt: generateTimestamp()
    };
    users.push(user);
  }

  // Create JWT token (no password verification needed)
  const token = jwt.sign(
    { id: user.id, email: user.email, name: user.name },
    JWT_SECRET,
    { expiresIn: '24h' }
  );

  // Return user data with token
  const { password: _, ...userWithoutPassword } = user;
  res.json({
    user: userWithoutPassword,
    token
  });
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
app.listen(PORT, () => {
  console.log(`Mock API server is running on http://localhost:${PORT}`);
});
