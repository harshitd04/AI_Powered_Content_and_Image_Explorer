# AI Content Explorer - Frontend

A modern React frontend for the AI Content Explorer platform, featuring AI-powered search and image generation capabilities.

## Features

- 🔐 **Authentication**: Secure login/register with JWT tokens
- 🔍 **AI Search**: Intelligent web search using DuckDuckGo MCP server
- 🎨 **Image Generation**: AI-powered image creation with Flux ImageGen
- 📊 **Dashboard**: Personal dashboard with search/image history
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Responsive**: Mobile-friendly design with Tailwind CSS
- ⚡ **Modern UI**: Clean, minimalistic interface with smooth animations

## Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Heroicons** - Beautiful SVG icons
- **Axios** - HTTP client for API calls
- **Context API** - State management for auth and theme

## Prerequisites

- Node.js 16+ and npm
- Backend server running on `http://localhost:8000`

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.js       # Main layout wrapper
│   ├── Navbar.js       # Top navigation bar
│   ├── Sidebar.js      # Side navigation
│   ├── LoadingSpinner.js
│   └── ProtectedRoute.js
├── contexts/           # React Context providers
│   ├── AuthContext.js  # Authentication state
│   └── ThemeContext.js # Theme management
├── pages/              # Main application pages
│   ├── Login.js        # Login page
│   ├── Register.js     # Registration page
│   ├── Dashboard.js    # User dashboard
│   ├── Search.js       # Search interface
│   └── ImageGeneration.js # Image generation
├── App.js              # Main app component
├── index.js            # React entry point
└── index.css           # Global styles
```

## Key Features

### Authentication
- JWT-based authentication with automatic token refresh
- Protected routes that redirect to login
- User profile management
- Secure logout functionality

### Search Interface
- Real-time web search using AI
- Configurable result limits (5-50 results)
- Save search results to dashboard
- Clean, readable result display
- Error handling and loading states

### Image Generation
- AI-powered image creation from text prompts
- Customizable parameters (width, height, quality steps)
- Preset prompt suggestions
- Image download functionality
- Save generated images to dashboard

### Dashboard
- Personal statistics and activity overview
- Recent searches and images history
- Filter and manage saved content
- Delete unwanted entries
- Responsive grid layout

### Theme System
- Light/dark mode toggle
- System preference detection
- Persistent theme selection
- Smooth transitions between themes

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication**: `/auth/login`, `/auth/register`, `/auth/profile`
- **Search**: `/search` - AI-powered web search
- **Images**: `/image` - AI image generation
- **Dashboard**: `/dashboard` - User data and statistics
- **Management**: Delete endpoints for searches and images

## Styling

Built with Tailwind CSS featuring:
- Custom color palette with primary blue theme
- Dark mode support with `dark:` variants
- Responsive design with mobile-first approach
- Custom animations and transitions
- Reusable component classes

## Environment Setup

The app expects the backend to be running on `http://localhost:8000`. This is configured via the `proxy` field in `package.json`.

For production, update the API base URL in the axios configuration.

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style

- Functional components with hooks
- Context API for global state
- Consistent error handling
- Loading states for all async operations
- Responsive design patterns
- Accessible UI components

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.