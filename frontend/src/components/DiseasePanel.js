import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DiseasePanel.css';

const DiseasePanel = ({ selectedLanguage }) => {
  const [diseases, setDiseases] = useState([]);
  const [selectedDisease, setSelectedDisease] = useState(null);
  const [diseaseInfo, setDiseaseInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch disease list on component mount and language change
  useEffect(() => {
    const fetchDiseaseList = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:5000/api/diseases?lang=${selectedLanguage}`);
        setDiseases(response.data.diseases);
      } catch (error) {
        console.error('Error fetching disease list:', error);
        // Fallback disease list
        setDiseases([
          { key: 'covid19', name: getTranslatedName('COVID-19') },
          { key: 'dengue', name: getTranslatedName('Dengue') },
          { key: 'malaria', name: getTranslatedName('Malaria') },
          { key: 'diabetes', name: getTranslatedName('Diabetes') },
          { key: 'typhoid', name: getTranslatedName('Typhoid') }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDiseaseList();
  }, [selectedLanguage]);

  const getTranslatedName = (diseaseName) => {
    const translations = {
      'en': { 'COVID-19': 'COVID-19', 'Dengue': 'Dengue', 'Malaria': 'Malaria', 'Diabetes': 'Diabetes', 'Typhoid': 'Typhoid' },
      'hi': { 'COVID-19': 'कोविड-19', 'Dengue': 'डेंगू', 'Malaria': 'मलेरिया', 'Diabetes': 'मधुमेह', 'Typhoid': 'टाइफाइड' },
      'mr': { 'COVID-19': 'कोविड-19', 'Dengue': 'डेंग्यू', 'Malaria': 'मलेरिया', 'Diabetes': 'मधुमेह', 'Typhoid': 'टायफॉइड' },
      'ta': { 'COVID-19': 'கோவிட்-19', 'Dengue': 'டெங்கு', 'Malaria': 'மலேரியா', 'Diabetes': 'நீரிழிவு', 'Typhoid': 'டைபாய்டு' },
      'te': { 'COVID-19': 'కోవిడ్-19', 'Dengue': 'డెంగ్యూ', 'Malaria': 'మలేరియా', 'Diabetes': 'మధుమేహం', 'Typhoid': 'టైఫాయిడ్' },
      'bn': { 'COVID-19': 'কোভিড-১৯', 'Dengue': 'ডেঙ্গু', 'Malaria': 'ম্যালেরিয়া', 'Diabetes': 'ডায়াবেটিস', 'Typhoid': 'টাইফয়েড' }
    };
    return translations[selectedLanguage]?.[diseaseName] || diseaseName;
  };

  const fetchDiseaseInfo = async (diseaseKey) => {
    setIsLoading(true);
    setSelectedDisease(diseaseKey);
    try {
      const response = await axios.get(`http://localhost:5000/api/disease/${diseaseKey}?lang=${selectedLanguage}`);
      setDiseaseInfo(response.data.disease);
    } catch (error) {
      console.error('Error fetching disease info:', error);
      // Fallback info
      setDiseaseInfo(getFallbackInfo(diseaseKey));
    } finally {
      setIsLoading(false);
    }
  };

  const getFallbackInfo = (diseaseKey) => {
    const fallback = {
      covid19: {
        name: 'COVID-19',
        symptoms: ['Fever', 'Cough', 'Difficulty breathing', 'Fatigue', 'Loss of taste/smell'],
        prevention: ['Wear mask', 'Maintain distance', 'Wash hands', 'Get vaccinated'],
        when_to_see_doctor: 'Difficulty breathing, chest pain, confusion'
      },
      dengue: {
        name: 'Dengue',
        symptoms: ['High fever', 'Severe headache', 'Joint pain', 'Nausea', 'Skin rash'],
        prevention: ['Prevent mosquito bites', 'Remove standing water', 'Use mosquito nets'],
        when_to_see_doctor: 'High fever with severe headache or pain behind eyes'
      },
      malaria: {
        name: 'Malaria',
        symptoms: ['High fever', 'Chills', 'Sweating', 'Headache', 'Muscle pain'],
        prevention: ['Mosquito repellent', 'Bed nets', 'Remove standing water'],
        when_to_see_doctor: 'Fever with chills, especially after travel'
      },
      diabetes: {
        name: 'Diabetes',
        symptoms: ['Increased thirst', 'Frequent urination', 'Extreme hunger', 'Blurred vision'],
        prevention: ['Healthy diet', 'Regular exercise', 'Maintain healthy weight'],
        when_to_see_doctor: 'Experiencing symptoms or have risk factors'
      },
      typhoid: {
        name: 'Typhoid',
        symptoms: ['Prolonged fever', 'Headache', 'Stomach pain', 'Loss of appetite'],
        prevention: ['Get vaccinated', 'Drink clean water', 'Wash hands frequently'],
        when_to_see_doctor: 'Fever persists >3 days or severe abdominal pain'
      }
    };
    return fallback[diseaseKey] || fallback.covid19;
  };

  const filteredDiseases = diseases.filter(disease =>
    disease.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="disease-panel">
      <div className="panel-header">
        <h3>📚 Disease Awareness</h3>
        <p>Learn about symptoms, prevention & care</p>
      </div>

      <div className="search-box">
        <input
          type="text"
          placeholder={getSearchPlaceholder(selectedLanguage)}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <span className="search-icon">🔍</span>
      </div>

      <div className="disease-list">
        {isLoading && filteredDiseases.length === 0 ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading diseases...</p>
          </div>
        ) : (
          filteredDiseases.map((disease) => (
            <button
              key={disease.key}
              className={`disease-item ${selectedDisease === disease.key ? 'active' : ''}`}
              onClick={() => fetchDiseaseInfo(disease.key)}
            >
              <span className="disease-icon">🩺</span>
              <span className="disease-name">{disease.name}</span>
            </button>
          ))
        )}
        {filteredDiseases.length === 0 && !isLoading && (
          <div className="no-results">
            <p>No diseases found</p>
          </div>
        )}
      </div>

      {diseaseInfo && (
        <div className="disease-info">
          <div className="info-header">
            <h4>{diseaseInfo.name}</h4>
            <button className="close-info" onClick={() => setDiseaseInfo(null)}>✕</button>
          </div>
          
          <div className="info-section">
            <h5>📋 Symptoms</h5>
            <ul>
              {diseaseInfo.symptoms?.map((symptom, idx) => (
                <li key={idx}>{symptom}</li>
              ))}
            </ul>
          </div>

          <div className="info-section">
            <h5>🛡️ Prevention</h5>
            <ul>
              {diseaseInfo.prevention?.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          {diseaseInfo.basic_care && (
            <div className="info-section">
              <h5>💚 Basic Care</h5>
              <ul>
                {diseaseInfo.basic_care?.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="info-section warning">
            <h5>⚠️ When to See Doctor</h5>
            <p>{diseaseInfo.when_to_see_doctor}</p>
          </div>

          <div className="info-disclaimer">
            <small>⚠️ This information is for awareness only. Always consult a doctor.</small>
          </div>
        </div>
      )}
    </div>
  );
};

const getSearchPlaceholder = (lang) => {
  const placeholders = {
    'en': 'Search diseases...',
    'hi': 'बीमारियों को खोजें...',
    'mr': 'रोग शोधा...',
    'ta': 'நோய்களைத் தேடுங்கள்...',
    'te': 'வ్యాధிகளைத் தேடுங்கள்...',
    'bn': 'রোগ অনুসন্ধান করুন...'
  };
  return placeholders[lang] || placeholders['en'];
};

export default DiseasePanel;