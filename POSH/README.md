# POSH Video Generation System

A comprehensive system for generating educational POSH (Prevention of Sexual Harassment) training videos using Google's Gemini 2.5 Flash and Veo 3.0 models with LangGraph workflow orchestration.

## 🎯 Features

- **Multi-Step Video Generation**: Breaks down scenarios into 8-second scenes for 60-90 second training videos
- **AI-Powered Scene Creation**: Uses Gemini 2.5 Flash to intelligently structure scenarios
- **Professional Video Output**: Generates high-quality 720p videos with audio using Veo 3.0
- **Automated Workflow**: LangGraph orchestrates the entire process from input to final video
- **Educational Focus**: Specifically designed for workplace harassment prevention training

## 🏗️ System Architecture

```
User Scenario Input
        ↓
[Gemini 2.5 Flash] → Break into 8-second scenes
        ↓
[LangGraph Workflow] → Orchestrate generation process
        ↓
[Veo 3.0] → Generate individual scene videos (with audio)
        ↓
[Video Combiner] → Merge scenes into final 60-90s video
        ↓
Final POSH Training Video
```

## 📋 Requirements

- Python 3.8+
- Conda environment named 'POSH'
- Google Gemini API Key
- FFmpeg (for video processing)

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Activate the POSH conda environment
conda activate POSH

# Install dependencies
python setup.py
```

### 2. Configuration

Ensure your `.env` file contains:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Run the Application

#### Option A: Web Interface (Recommended)
```bash
# Launch beautiful Streamlit web interface
python run_streamlit.py
# OR double-click run_streamlit.bat (Windows)
```

#### Option B: Command Line Interface
```bash
python main.py
```

## 💡 Usage Examples

### Interactive Mode
```bash
python main.py
```
Follow the prompts to enter your POSH scenario.

### Batch Mode
```bash
python main.py scenario.txt
```
Process a scenario from a text file.

### Example Scenario Input
```
A manager repeatedly making inappropriate comments to a junior employee 
during team meetings, making them uncomfortable. The scenario shows other 
colleagues noticing and the proper way to report and address such behavior 
through HR channels.
```

## 🔧 Configuration

### `config.py` Settings
- **VIDEO_DURATION_SECONDS**: 8 (fixed for Veo 3.0)
- **TARGET_TOTAL_DURATION**: (60, 90) seconds
- **VIDEO_RESOLUTION**: "720p"
- **SCENARIO_MODEL**: "gemini-2.0-flash-exp"
- **VIDEO_MODEL**: "veo-3.0-generate-001"

## 📁 Project Structure

```
POSH/
├── main.py                 # Main application entry point
├── workflow.py             # LangGraph workflow orchestration
├── scenario_processor.py   # Gemini 2.5 Flash scenario breakdown
├── video_generator.py      # Veo 3.0 video generation
├── video_combiner.py       # Video concatenation and effects
├── models.py               # Pydantic data models
├── config.py               # Configuration settings
├── setup.py                # Installation script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── generated_videos/       # Final output videos
└── temp_scenes/            # Temporary scene videos
```

## 🎬 Video Generation Process

1. **Scenario Processing**: User input → structured scenes with Gemini 2.5 Flash
2. **Scene Validation**: Ensure 8-second duration and educational content
3. **Video Generation**: Each scene → Veo 3.0 → 8-second video with audio
4. **Individual Review**: Each 8-second video saved separately for review
5. **Output**: Professional POSH training videos ready for use

## 🌐 Streamlit Web Interface Features

### **Beautiful User Experience**
- Clean, modern web interface
- Real-time progress tracking
- Interactive scenario input with examples
- Visual scene breakdown display

### **Three-Step Workflow**
1. **📝 Scenario Input**: Paste or select example scenarios
2. **📋 Scene Showcase**: View AI-generated scene breakdown
3. **🎬 Video Display**: Watch generated videos directly in browser

### **Advanced Features**
- Pre-loaded example scenarios
- Scene-by-scene video playback
- Download links for all videos
- Progress bars and status updates
- Responsive design for all devices

## 📊 Output Features

- **Intro Slide**: Scenario title and context
- **Scene Titles**: Each scene labeled with setting
- **Professional Audio**: Appropriate dialogue and tone
- **Outro Slide**: Key learning objectives
- **High Quality**: 720p resolution, 24fps

## 🛠️ Dependencies

### Core Libraries
- `google-genai`: Google AI API integration
- `langchain`: LLM framework
- `langgraph`: Workflow orchestration
- `moviepy`: Video processing
- `pydantic`: Data validation

### System Requirements
- FFmpeg for video processing
- Sufficient disk space for video files
- Stable internet connection for API calls

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: GEMINI_API_KEY not found
   ```
   - Ensure `.env` file contains valid API key
   - Get key from: https://ai.google.dev/

2. **Video Generation Timeout**
   - Veo 3.0 can take 11 seconds to 6 minutes
   - Check internet connection
   - Retry with simpler scenarios

3. **Memory Issues**
   - Large video files may require more RAM
   - Close other applications during processing

4. **FFmpeg Not Found**
   ```bash
   # Install FFmpeg
   conda install ffmpeg
   ```

## 📈 Performance Tips

- **Scenario Length**: Keep descriptions detailed but concise
- **Character Descriptions**: Include appearance and roles
- **Setting Details**: Specify workplace environments clearly
- **Dialogue**: Write natural, professional conversations

## 🔒 Safety and Ethics

- Content is filtered for appropriate workplace training
- Generated videos include educational disclaimers
- Scenarios focus on prevention and proper reporting
- All content designed for professional development

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration settings
3. Ensure all dependencies are installed
4. Verify API key is valid and has sufficient quota

## 🔗 Related Links

- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Veo 3.0 Video Generation Guide](https://ai.google.dev/gemini-api/docs/video)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [POSH Guidelines and Best Practices](https://www.eeoc.gov/harassment)

---

**Note**: This system generates educational content for workplace training. Always review generated videos for appropriateness and compliance with your organization's policies before use.
