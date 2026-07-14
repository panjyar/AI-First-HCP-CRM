import { useEffect } from "react";
import { useAppDispatch } from "./app/hooks";
import { AppHeader } from "./components/AppHeader";
import { ChatPanel } from "./components/ChatPanel";
import { InteractionPanel } from "./components/InteractionPanel";
import { initializeCRM } from "./features/crm/crmSlice";

function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    void dispatch(initializeCRM());
  }, [dispatch]);

  return (
    <div className="app-shell">
      <AppHeader />
      <div className="workspace">
        <InteractionPanel />
        <ChatPanel />
      </div>
    </div>
  );
}

export default App;
