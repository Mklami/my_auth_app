const { initializeApp } = require('firebase-admin/app');
const { getFirestore } = require('firebase-admin/firestore');
const { onDocumentCreated } = require('firebase-functions/v2/firestore');
const { logger } = require('firebase-functions');
const nodemailer = require('nodemailer');

// Initialize Firebase Admin
initializeApp();
const db = getFirestore();

// Configure nodemailer
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'mayasa.naama@gmail.com',
    pass: 'tzez zlux zwqk wbbg', // App password
  },
});

// Cloud Function
exports.sendSurveyEmail = onDocumentCreated('survey_responses/{docId}', async (event) => {
  const data = event.data.data();

  const mailOptions = {
    from: 'mayasa.naama@gmail.com',
    to: data.recipientEmail || 'mayasa.naama@gmail.com',
    subject: 'New AI Survey Submitted ✅',
    html: `
      <p><strong>Name:</strong> ${data.name}</p>
      <p><strong>Birth Date:</strong> ${data.birthDate}</p>
      <p><strong>Education:</strong> ${data.educationLevel}</p>
      <p><strong>City:</strong> ${data.city}</p>
      <p><strong>Gender:</strong> ${data.gender}</p>
      <p><strong>AI Models:</strong></p>
      <ul>
        ${data.aiModels.map(model => `<li>${model.model}: ${model.defects}</li>`).join('')}
      </ul>
      <p><strong>Use Case:</strong> ${data.beneficialUseCase}</p>
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    logger.info('✅ Email sent successfully to', mailOptions.to);
  } catch (error) {
    logger.error('❌ Error sending email:', error);
  }
});
