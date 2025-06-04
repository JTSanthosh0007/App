'use client';

import { useRouter } from 'next/navigation';

export default function PrivacyPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-black flex flex-col items-center py-8">
      <div className="w-full max-w-sm bg-zinc-900 rounded-xl shadow-lg p-6 mt-4">
        <button onClick={() => router.back()} className="mb-4 text-white flex items-center gap-2 hover:text-blue-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="font-semibold">Privacy</span>
        </button>
        <h1 className="text-xl font-bold text-white mb-4">Privacy Policy</h1>
        <div className="text-zinc-200 text-sm space-y-4 max-h-[70vh] overflow-y-auto pr-2">
          <div>
            <h2 className="font-semibold text-base text-white mb-1">Introduction</h2>
            <p>Welcome to our app! We are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, store, and protect your data when you use our services. By using our app, you agree to the terms outlined in this policy.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">1. Information We Collect</h2>
            <h3 className="font-semibold text-zinc-100 mt-2">a. Information You Provide</h3>
            <ul className="list-disc ml-5">
              <li>Name: To personalize your experience.</li>
              <li>Email Address: For account creation, communication, and support.</li>
              <li>Phone Number: For account verification and support.</li>
              <li>Profile Picture: If you choose to upload one.</li>
              <li>Bank Statement Data: If you upload or analyze bank statements, we process the data solely for the purpose of providing you with insights and analytics.</li>
            </ul>
            <h3 className="font-semibold text-zinc-100 mt-2">b. Information We Collect Automatically</h3>
            <ul className="list-disc ml-5">
              <li>Device Information: Type of device, operating system, and browser.</li>
              <li>Usage Data: How you interact with the app, including features used, pages visited, and time spent.</li>
              <li>Log Data: IP address, access times, and error logs for security and troubleshooting.</li>
            </ul>
            <h3 className="font-semibold text-zinc-100 mt-2">c. Cookies and Tracking Technologies</h3>
            <p>We may use cookies and similar technologies to enhance your experience, remember your preferences, and analyze app usage. You can control cookies through your browser settings.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">2. How We Use Your Information</h2>
            <ul className="list-disc ml-5">
              <li>Provide, operate, and maintain the app.</li>
              <li>Personalize your experience and deliver relevant content.</li>
              <li>Analyze usage and improve our services.</li>
              <li>Communicate with you about updates, support, and important notices.</li>
              <li>Ensure the security and integrity of our app.</li>
              <li>Comply with legal obligations.</li>
            </ul>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">3. Data Security</h2>
            <p>We take your data security seriously. We implement industry-standard security measures to protect your information from unauthorized access, disclosure, alteration, or destruction. These measures include:</p>
            <ul className="list-disc ml-5">
              <li>Encryption: Sensitive data is encrypted both in transit and at rest.</li>
              <li>Access Controls: Only authorized personnel have access to your data.</li>
              <li>Regular Security Audits: We regularly review our security practices and update them as needed.</li>
              <li>Secure Servers: Data is stored on secure servers with robust firewalls.</li>
            </ul>
            <p>Despite our best efforts, no method of transmission over the internet or electronic storage is 100% secure. We cannot guarantee absolute security, but we strive to use commercially acceptable means to protect your information.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">4. Data Retention</h2>
            <p>We retain your personal information only as long as necessary to fulfill the purposes outlined in this policy, comply with legal obligations, resolve disputes, and enforce our agreements. When your data is no longer needed, we securely delete or anonymize it.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">5. Sharing and Disclosure</h2>
            <p>We do <span className="font-bold">not</span> sell, trade, or rent your personal information to third parties. We may share your information only in the following circumstances:</p>
            <ul className="list-disc ml-5">
              <li>With Your Consent: If you give us explicit permission.</li>
              <li>Service Providers: We may engage trusted third-party service providers to assist in operating our app, such as cloud hosting or analytics. These providers are contractually obligated to protect your data and use it only for the services we request.</li>
              <li>Legal Requirements: We may disclose your information if required by law, regulation, or legal process, or to protect the rights, property, or safety of our users or others.</li>
            </ul>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">6. Your Rights and Choices</h2>
            <p>You have the following rights regarding your personal information:</p>
            <ul className="list-disc ml-5">
              <li>Access: You can request access to the personal data we hold about you.</li>
              <li>Correction: You can request corrections to inaccurate or incomplete data.</li>
              <li>Deletion: You can request deletion of your data, subject to legal and contractual obligations.</li>
              <li>Restriction: You can request that we restrict the processing of your data in certain circumstances.</li>
              <li>Objection: You can object to our processing of your data for certain purposes.</li>
              <li>Portability: You can request a copy of your data in a structured, commonly used, and machine-readable format.</li>
            </ul>
            <p>To exercise any of these rights, please contact us at <span className="text-blue-400">support@example.com</span>.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">7. Children's Privacy</h2>
            <p>Our app is not intended for children under the age of 13. We do not knowingly collect personal information from children. If you believe a child has provided us with personal information, please contact us, and we will take steps to delete such information.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">8. International Data Transfers</h2>
            <p>If you are accessing our app from outside your country of residence, your information may be transferred to, stored, and processed in a country with different data protection laws. We take appropriate measures to ensure your data is protected in accordance with this policy.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">9. Third-Party Links and Services</h2>
            <p>Our app may contain links to third-party websites or services. We are not responsible for the privacy practices or content of those third parties. We encourage you to review their privacy policies before providing any information.</p>
          </div>
          <div>
            <h2 className="font-semibold text-base text-white mb-1">10. Changes to This Privacy Policy</h2>
            <p>We may update this Privacy Policy from time to time to reflect changes in our practices, technology, or legal requirements. We will notify you of any significant changes by posting the new policy on this page and updating the effective date. Your continued use of the app after changes are made constitutes your acceptance of the new policy.</p>
          </div>
        </div>
      </div>
    </div>
  );
} 