# Bot\build\code\cli\next\utils\nextBuilder\frontend\public\components\landing_ui_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

PUBLIC_MAIN_PAGE_TEMPLATE = """
import Link from 'next/link';  // Import Link for client-side navigation

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-6xl font-bold">
          Welcome to <a className="text-blue-600" href="/home">Flex Data</a>
        </h1>

        <p className="mt-3 text-2xl">
          State of the Art AI SAAS.
        </p>

        {/* Action Button */}
        <Link href="/llm">
          <span className="mt-10 text-white bg-blue-500 hover:bg-blue-700 font-bold py-2 px-4 rounded">
            Get Started
          </span>
        </Link>
      </main>
    </div>
  );
}
"""

create_component('LandingComponent', PUBLIC_MAIN_PAGE_TEMPLATE)

