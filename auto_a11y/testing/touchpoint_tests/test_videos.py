"""
Videos touchpoint test module
Evaluates the presence and accessibility of video elements on the page.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Video Accessibility Analysis",
    "touchpoint": "videos",
    "description": "Evaluates the presence and accessibility of video elements on the page, including native HTML5 videos and embedded players from services like YouTube and Vimeo. This test specifically checks for required title attributes on iframe-embedded videos.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.1", "4.1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.5", "2.1.1"],
    "tests": [
        {
            "id": "iframe-title",
            "name": "Iframe Title Attribute",
            "description": "Checks if embedded videos using iframes have title attributes that describe their content.",
            "impact": "high",
            "wcagCriteria": ["2.4.1", "4.1.2"],
        },
        {
            "id": "video-identification",
            "name": "Video Identification",
            "description": "Identifies all video content on the page, including native HTML5 videos and common embedded players.",
            "impact": "informational",
            "wcagCriteria": ["1.2.1", "1.2.2", "1.2.3", "1.2.5"],
        },
        {
            "id": "native-video-controls",
            "name": "Native Video Controls",
            "description": "Checks if native HTML5 video elements have controls attribute enabled.",
            "impact": "high",
            "wcagCriteria": ["2.1.1"],
        },
        {
            "id": "video-player-accessibility",
            "name": "Video Player Accessibility",
            "description": "Evaluates if video players have accessible controls and attributes.",
            "impact": "high",
            "wcagCriteria": ["1.2.1", "1.2.2", "2.1.1"],
        }
    ]
}

async def test_videos(page) -> Dict[str, Any]:
    """
    Test for presence of videos and their accessibility features
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze videos
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'videos',
                    checks: []
                };
                
                // Function to generate XPath for elements
                function getFullXPath(element) {
                    if (!element) return '';
                    
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) {
                                count++;
                            }
                        }
                        return count;
                    }
                    
                    let path = '';
                    while (element && element.nodeType === 1) {
                        const idx = getElementIdx(element);
                        const tagName = element.tagName.toLowerCase();
                        path = `/${tagName}[${idx}]${path}`;
                        element = element.parentNode;
                    }
                    return path;
                }
                
                // Identify video type from element
                function getVideoType(element) {
                    const tag = element.tagName.toLowerCase();
                    if (tag === 'video') return 'Native HTML5';
                    if (tag === 'iframe') {
                        const src = element.src || '';
                        if (src.includes('youtube.com') || src.includes('youtu.be')) return 'YouTube';
                        if (src.includes('vimeo.com')) return 'Vimeo';
                        if (src.includes('dailymotion.com')) return 'Dailymotion';
                        if (src.includes('facebook.com/plugins/video')) return 'Facebook';
                        return 'Iframe Video';
                    }
                    return 'Custom Player';
                }
                
                // Get video URL
                function getVideoUrl(element, type) {
                    if (element.src) return element.src;
                    if (element.querySelector('source')) {
                        return element.querySelector('source').src;
                    }
                    return null;
                }
                
                // Get video name/title
                function getVideoName(element, type) {
                    if (element.tagName.toLowerCase() === 'iframe') {
                        const iframeTitle = element.getAttribute('title');
                        if (!iframeTitle) {
                            return null; // Indicates missing required title
                        }
                        return iframeTitle;
                    }

                    const possibleNames = [
                        element.getAttribute('title'),
                        element.getAttribute('aria-label'),
                        element.getAttribute('alt'),
                        element.getAttribute('data-title')
                    ].filter(Boolean);

                    if (type === 'YouTube' && !possibleNames.length) {
                        const src = element.src || '';
                        const videoId = src.match(/(?:youtube\\.com\\/(?:[^\\/]+\\/.+\\/|(?:v|e(?:mbed)?)\\/|.*[?&]v=)|youtu\\.be\\/)([^"&?\\/\\s]{11})/i);
                        if (videoId) {
                            return `YouTube video ID: ${videoId[1]}`;
                        }
                    }

                    if (type === 'Vimeo' && !possibleNames.length) {
                        const src = element.src || '';
                        const videoId = src.match(/vimeo\\.com\\/(?:video\\/)?([0-9]+)/i);
                        if (videoId) {
                            return `Vimeo video ID: ${videoId[1]}`;
                        }
                    }

                    return possibleNames[0] || 'Untitled video';
                }
                
                // Find native video elements
                const nativeVideos = Array.from(document.getElementsByTagName('video'));
                
                // Find iframes that might contain videos
                const iframeVideos = Array.from(document.getElementsByTagName('iframe'))
                    .filter(iframe => {
                        const src = iframe.src || '';
                        return src.includes('youtube.com') || 
                               src.includes('youtu.be') ||
                               src.includes('vimeo.com') ||
                               src.includes('dailymotion.com') ||
                               src.includes('facebook.com/plugins/video') ||
                               src.includes('brightcove') ||
                               src.includes('kaltura');
                    });

                // Find other potential video players
                const otherPlayers = Array.from(document.querySelectorAll(
                    '.video-js, .jwplayer, .plyr, [data-player-type="video"]'
                ));
                
                const allVideos = [...nativeVideos, ...iframeVideos, ...otherPlayers];
                
                if (allVideos.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No videos found on the page';
                    return results;
                }
                
                results.elements_tested = allVideos.length;
                
                let iframesWithoutTitles = 0;
                let nativeVideosWithoutControls = 0;
                
                // Process all video elements
                allVideos.forEach(element => {
                    const type = getVideoType(element);
                    const isIframe = element.tagName.toLowerCase() === 'iframe';
                    const isNative = element.tagName.toLowerCase() === 'video';
                    const name = getVideoName(element, type);
                    
                    let hasViolation = false;
                    
                    // Check iframe title violations
                    if (isIframe && !element.getAttribute('title')) {
                        iframesWithoutTitles++;
                        results.errors.push({
                            err: 'ErrVideoIframeMissingTitle',
                            type: 'err',
                            cat: 'videos',
                            element: 'iframe',
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Video iframe is missing a descriptive title attribute',
                            videoType: type,
                            url: element.src
                        });
                        hasViolation = true;
                    }
                    
                    // Check native video controls
                    if (isNative && !element.hasAttribute('controls')) {
                        nativeVideosWithoutControls++;
                        results.errors.push({
                            err: 'ErrNativeVideoMissingControls',
                            type: 'err',
                            cat: 'videos',
                            element: 'video',
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Native HTML5 video element is missing controls attribute',
                            src: element.src || element.querySelector('source')?.src || 'unknown'
                        });
                        hasViolation = true;
                    }
                    
                    // Check for autoplay (accessibility concern)
                    if (isNative && element.hasAttribute('autoplay')) {
                        results.warnings.push({
                            err: 'WarnVideoAutoplay',
                            type: 'warn',
                            cat: 'videos',
                            element: 'video',
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Video has autoplay attribute which can cause accessibility issues'
                        });
                    }
                    
                    if (!hasViolation) {
                        results.elements_passed++;
                    } else {
                        results.elements_failed++;
                    }
                });
                
                // Add check information for reporting
                if (iframeVideos.length > 0) {
                    results.checks.push({
                        description: 'Video iframe titles',
                        wcag: ['2.4.1', '4.1.2'],
                        total: iframeVideos.length,
                        passed: iframeVideos.length - iframesWithoutTitles,
                        failed: iframesWithoutTitles
                    });
                }
                
                if (nativeVideos.length > 0) {
                    results.checks.push({
                        description: 'Native video controls',
                        wcag: ['2.1.1'],
                        total: nativeVideos.length,
                        passed: nativeVideos.length - nativeVideosWithoutControls,
                        failed: nativeVideosWithoutControls
                    });
                }
                
                results.checks.push({
                    description: 'Video accessibility (informational)',
                    wcag: ['1.2.1', '1.2.2', '1.2.3'],
                    total: allVideos.length,
                    passed: 0, // Informational only
                    failed: 0
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_videos: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }