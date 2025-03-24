// File: app/appgen/src/app/api/apps/route.ts

import { NextRequest, NextResponse } from "next/server";
import path from "path";
import { promises as fs } from "fs";

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
	try {
		// Define the directory where projects are stored.
		const projectsDir = path.join(process.cwd(), "../..");

		// Read all entries in the projects folder.
		const entries = await fs.readdir(projectsDir);

		// Get metadata for each entry.
		const projects = await Promise.all(
			entries.map(async (entry) => {
				const fullPath = path.join(projectsDir, entry);
				const stat = await fs.stat(fullPath);
				return {
					name: entry,
					isDirectory: stat.isDirectory(),
					size: stat.size,
					createdAt: stat.birthtime, // or stat.ctime if preferred
				};
			})
		);

		// Filter to include only directories (assuming each project is a folder).
		let filteredProjects = projects.filter((p) => p.isDirectory);

		// Read the 'view' query parameter (e.g. trending).
		const view = request.nextUrl.searchParams.get("view") || "all";

		// If view is trending, filter projects created within the last 24 hours and sort descending by creation date.
		if (view === "trending") {
			const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
			filteredProjects = filteredProjects.filter(
				(project) => new Date(project.createdAt) >= twentyFourHoursAgo
			);
			filteredProjects.sort(
				(a, b) =>
					new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
			);
		}

		return NextResponse.json(filteredProjects);
	} catch (error) {
		console.error("Error reading projects:", error);
		return NextResponse.json(
			{ error: "Failed to read projects" },
			{ status: 500 }
		);
	}
}
