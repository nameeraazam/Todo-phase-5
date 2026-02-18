import { LogOut, User, CheckSquare } from 'lucide-react';

export default function Navbar({ user, onLogout }) {
  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <CheckSquare className="h-8 w-8 text-primary-600" />
            <span className="ml-3 text-xl font-bold text-gray-900">Todo App</span>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-gray-700">
              <User className="h-5 w-5" />
              <span className="font-medium">{user?.name || user?.email}</span>
            </div>
            
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 text-red-600 hover:text-red-700 transition-colors"
            >
              <LogOut className="h-5 w-5" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
