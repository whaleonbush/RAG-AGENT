import { Route, Routes } from "react-router-dom";
import ProjectListPage from "./pages/ProjectListPage";
import ProjectWorkspacePage from "./pages/ProjectWorkspacePage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
    </Routes>
  );
}
