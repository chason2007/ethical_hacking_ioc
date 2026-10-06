import { useState, useEffect } from 'react';
import { api } from './services/api';
import type { Capture } from './types';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { UploadModal } from './components/captures/UploadModal';

import { DashboardPage } from './pages/DashboardPage';
import { PacketExplorerPage } from './pages/PacketExplorerPage';
import { ProtocolsPage } from './pages/ProtocolsPage';
import { ConversationsPage } from './pages/ConversationsPage';
import { EndpointsPage } from './pages/EndpointsPage';
import { PortsPage } from './pages/PortsPage';
import { SecurityInsightsPage } from './pages/SecurityInsightsPage';
import { TimelinePage } from './pages/TimelinePage';
import { ReportsPage } from './pages/ReportsPage';
import { CapturesPage } from './pages/CapturesPage';
import { EducationalPage } from './pages/EducationalPage';

export function App() {
  const [captures, setCaptures] = useState<Capture[]>([]);
  const [currentCapture, setCurrentCapture] = useState<Capture | null>(null);
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isLoadingDemo, setIsLoadingDemo] = useState(false);
  const [backendHealthy, setBackendHealthy] = useState(true);
  const [findingsCount, setFindingsCount] = useState(0);

  const handleLoadDemo = async () => {
    setIsLoadingDemo(true);
    try {
      const demoCapture = await api.loadDemoCapture();
      const data = await api.getCaptures();
      setCaptures(data);
      setCurrentCapture(demoCapture);
      setCurrentTab('dashboard');
    } catch (err) {
      console.error('Failed to load demo:', err);
    } finally {
      setIsLoadingDemo(false);
    }
  };

  // Load initial captures & health status
  const loadCapturesList = async (selectLatest: boolean = false) => {
    try {
      const health = await api.getHealth();
      setBackendHealthy(health.status === 'healthy');

      const data = await api.getCaptures();
      setCaptures(data);

      if (data.length > 0) {
        if (!currentCapture || selectLatest) {
          setCurrentCapture(data[0]);
        } else {
          const existing = data.find((c) => c.id === currentCapture.id);
          setCurrentCapture(existing || data[0]);
        }
      } else {
        await handleLoadDemo();
      }
    } catch (err) {
      console.error('API connection failed:', err);
      setBackendHealthy(false);
    }
  };

  useEffect(() => {
    loadCapturesList();
  }, []);

  // Update findings count when active capture changes
  useEffect(() => {
    if (!currentCapture) return;
    api.getSecurity(currentCapture.id)
      .then((sec) => setFindingsCount(sec.total_findings))
      .catch(() => setFindingsCount(0));
  }, [currentCapture]);

  const handleUploadSuccess = (newCapture: Capture) => {
    loadCapturesList(true);
    setCurrentCapture(newCapture);
    setCurrentTab('dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      
      {/* Top Navigation */}
      <Navbar
        currentCapture={currentCapture}
        captures={captures}
        onSelectCapture={(cap) => setCurrentCapture(cap)}
        onOpenUpload={() => setIsUploadOpen(true)}
        onLoadDemo={handleLoadDemo}
        isLoadingDemo={isLoadingDemo}
        backendHealthy={backendHealthy}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Navigation Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onTabChange={(tab) => setCurrentTab(tab)}
          findingsCount={findingsCount}
        />

        {/* Dynamic Tab View Area */}
        <main className="flex-1 overflow-y-auto bg-slate-950/40">
          {currentTab === 'dashboard' && (
            <DashboardPage
              capture={currentCapture}
              onNavigateTab={(tab) => setCurrentTab(tab)}
            />
          )}

          {currentTab === 'packets' && (
            <PacketExplorerPage capture={currentCapture} />
          )}

          {currentTab === 'protocols' && (
            <ProtocolsPage capture={currentCapture} />
          )}

          {currentTab === 'conversations' && (
            <ConversationsPage capture={currentCapture} />
          )}

          {currentTab === 'endpoints' && (
            <EndpointsPage capture={currentCapture} />
          )}

          {currentTab === 'ports' && (
            <PortsPage capture={currentCapture} />
          )}

          {currentTab === 'security' && (
            <SecurityInsightsPage capture={currentCapture} />
          )}

          {currentTab === 'timeline' && (
            <TimelinePage capture={currentCapture} />
          )}

          {currentTab === 'reports' && (
            <ReportsPage capture={currentCapture} />
          )}

          {currentTab === 'captures' && (
            <CapturesPage
              currentCapture={currentCapture}
              onSelectCapture={(c) => setCurrentCapture(c)}
              onCapturesUpdated={() => loadCapturesList()}
            />
          )}

          {currentTab === 'educational' && (
            <EducationalPage />
          )}
        </main>

      </div>

      {/* Upload Capture Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onSuccess={handleUploadSuccess}
      />

    </div>
  );
}

export default App;
