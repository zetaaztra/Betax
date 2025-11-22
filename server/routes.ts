import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import path from "path";
import fs from "fs";

export async function registerRoutes(app: Express): Promise<Server> {
  app.get("/api/aegismatrix", (req, res) => {
    try {
      const dataPath = path.join(process.cwd(), "client", "public", "data", "aegismatrix.json");
      const data = JSON.parse(fs.readFileSync(dataPath, "utf-8"));
      res.json(data);
    } catch (error) {
      console.error("Error loading AegisMatrix data:", error);
      res.status(500).json({ error: "Failed to load market data" });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
