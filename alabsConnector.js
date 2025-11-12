function makeAbbrev(pageName) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < 4) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return pageName.slice(0, 4).replace(' ', '') + '-' + result;
}

function makeRnd(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return result;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function connector_get_status() {
    return globalThis.connector.status;
}

function connector_get_result() {
    console.log('returning result');
    return AlabsConnector.connector.connectorResult;
}

globalThis.requestQueue = new Array();
globalThis.connector = null;
globalThis.connector_status = 'Stopped';
globalThis.connectorResult = null;

async function run() {
    try {
        console.log("ALABS CONNECTOR THREAD")

        while (true) {

            while (globalThis.requestQueue.length > 0) {
                const request = globalThis.requestQueue.pop();
                console.log("ALABS CONNECTOR PROCESSING REQUEST");
                switch (request.reqId) {
                    case 'Close':
                        console.log('Connector closed');
                        return;
                    case "Init":
                        globalThis.connector = new AlabsConnector(request.server, request.user, request.pass, request.audit);
                        await globalThis.connector.updateTheConnection();
                        console.log('Initialized csrf: ' + globalThis.connector.csrf_token);
                        break;

                    case "Init":
                        globalThis.connector = new AlabsConnector(request.server, request.user, request.pass, request.audit);
                        await globalThis.connector.updateTheConnection();
                        console.log('Initialized csrf: ' + globalThis.connector.csrf_token);
                        break;

                    case 'CreateDiscoveredPage':
                        console.log('Creating discovered page');
                        await globalThis.connector.createDiscoveredPage(request.pageName, request.pageUrl, request.imgdir, request.pdfList);
                        console.log('Created discovered page');
                        break;

                    case 'CreateFailurePoint':
                        console.log('Creating failure point');
                        await globalThis.connector.createFailurePoint(request.pageName, request.pageUrl, request.pageId, request.pageAbbrev, request.failureType, request.xpath, request.tempId);
                        console.log('Created failure point');
                        break;
                    case 'GetFailurePoints':
                        console.log('Getting failure points by pageId');
                        await globalThis.connector.getFailurePoints(request.pageId);
                        console.log('Got failure points by pageId');
                        break;
                    case 'CreateIssue':
                        console.log('Creating Issue');
                        await globalThis.connector.createIssue(request.pageId, request.tempFpId, request.xpath, request.issueCode, request.isWarn, request.cat);
                        console.log('Created Issue');
                        break;
                    case 'CreateManualIssue':
                        console.log('Creating Manual Issue');
                        await globalThis.connector.createManualIssue(request.pageId, request.tempFpId, request.issueCode, request.transcript, request.screenshotUrl, request.timecode, request.videoId, request.note);
                        console.log('Created Manual Issue');

                    case 'GetIssueCategories':
                        console.log('Getting Issue Categories');
                        await globalThis.connector.getIssueCategories();
                        console.log('Got Issue Cateogories');
                        break;

                }
            }

            //console.log('...sleeping');
            await sleep(100);
        }

    } catch (e) {
        return console.log(e);
    }
}

run().then(console.log).catch(console.error);


class AlabsConnector {

    static currentServer = 'dev'; // default is dev
    static connectorResult = null;

    /////////////////////////////////////
    // Public interfaces
    /////////////////////////////////////

    static get_status() {
        return AlabsConnector.connector.status;
    }

    static get_result() {
        return AlabsConnector.connectorResult;
    }

    static async connector_init(server, user, pass, audit) {
        /*
        AlabsConnector.connector = new AlabsConnector(server, user, pass, audit);
        do await delay(500);
        while (AlabsConnector.get_status().ready === "initializing");
        return AlabsConnector.get_status();
        */
    }

    static connector_create_failure_point(pageName, pageUrl, pageId, pageAbbrev, pointType, xpath) {
        AlabsConnector.connector.createFailurePoint(pageName, pageUrl, pageId, pageAbbrev, pointType, xpath);
    }

    static async connector_update_discovered_pages(pageName, pageUrl, imgdir, pdfList) {
        AlabsConnector.connector.updateDiscoveredPages();
        do await delay(500);
        while (AlabsConnector.get_status().ready !== "ready");
        return AlabsConnector.get_status();

    }

    static connector_find_pageId_by_abbrev(pageAbbrev) {
        return AlabsConnector.connector.findPageIdByAbbrev(pageAbbrev);
    }

    ///////////////////////////////////
    // Private methods
    ///////////////////////////////////

    constructor(serverUrl, user, pass, audit) {

        this.serverUrl = serverUrl;
        this.audit = audit;
        this.user = user;
        this.pass = pass;
    }

    async updateTheConnection() {

        console.log('UpdateTheConnection');

        globalThis.connector_status = 'Busy';

        let myUrl = this.serverUrl + "/user/login?_format=json";
        await fetch(myUrl,
            {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                method: "POST",
                body: JSON.stringify({ name: this.user, pass: this.pass })

            })
            .then(response => {
                return response.json();
            })
            .then(json => {
                this.csrf_token = json.csrf_token;
            });

        // Get the current audits
        await this.getNodeSynchronous('rest/open_audits')
            .then(res => {
                this.auditList = res;
            });
        console.log('Num audits found: ' + this.auditList.length);

        console.log('testing for audit: ' + this.audit)

        // Ensure that the identified audit exists in the list
        let foundAudit = false;
        for (const a of this.auditList) {
            if (a.title === this.audit) {
                console.log('>> ' + a.title);
                foundAudit = true;
                this.auditNid = a.nid;
                this.auditUuid = a.uuId;
                this.auditAbbrev = a.field_abbreviation;
            }
        }
        if (!foundAudit) {
            console.log('Audit not found on server');
            this.status = 'err';
            this.err = 'Audit ' + this.audit + ' not found on server';
            globalThis.connector_status = 'Err';
            return;
        }

        console.log('Audit found');

        // Get the pages of the current audit
        await this.getNodeSynchronous('rest/discovered_pages', 'audit=' + this.auditNid)
            .then(res => {
                this.pageList = res;
            });

        console.log('Pages retrieved for current audit');

        // Get the issues for the current audit
        await this.getNodeSynchronous('rest/issues', 'audit=' + this.auditNid)
            .then(res => {
                this.issueList = res;
            });

        console.log('Issues for current audit retrieved');

        // Comment out for PROD
        // Get the failure point types
        await this.getNodeSynchronous('rest/failure_point_types')
            .then(res => {
                this.failurePointTypes = res;
            });

        // Get the issue categories
        await this.getNodeSynchronous('rest/issue_categories')
            .then(res => {
                console.log(">>> Got Categories")
                globalThis.issueCategories = res;
            });


        console.log('Issue categories retrieved');


        globalThis.connector_status = 'Ready';

    }

    async getNodeSynchronous(contentType, qualifier = '') {
        console.log('getNodeSynchronous called');
        const ftch = this.serverUrl + "/" + contentType + ((qualifier !== '') ? '?' : '') + qualifier + ((qualifier !== '') ? '&' : '?') + "_format=json";
        console.log(ftch);
        const response = await fetch(ftch,
            {
                headers: {
                    'Authorization': 'Basic ' + btoa(this.user + this.pass),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrf_token
                },
                method: "GET",
            })
            .catch(error => {
                console.log(error);
                return false;
            });

        const json = await response.json();
        return json;
    }

    async postNode(payload) {
        console.log('--- postNode');
        const response = await fetch(this.serverUrl + "/node?_format=json",
            {
                headers: {
                    'Authorization': 'Basic ' + btoa(this.user + ':' + this.pass),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': this.csrf_token
                },
                method: "POST",
                body: JSON.stringify(payload)
            });

        const json = await response.json();
        console.log('RETURN from fetch (full)');
        console.log(json)
        console.log('Return from fetch, nid: ' + json.nid[0].value);
        return json.nid[0].value;

    }

    async createDiscoveredPage(pageName, pageUrl, imgdir, pdfList) {

        console.log('begin creating discoved page');

        globalThis.connector_status = 'Busy';

        let drupalPdfList = [];
        pdfList.forEach(pdf => {
            drupalPdfList.push(
                { uri: pdf }
            );
        });

        const pageAbbrev = makeAbbrev(pageName);

        globalThis.currentPageDetails = { pageUrl: pageUrl, pageName: pageName, pageAbbrev: pageAbbrev };

        const payload = {
            "title": [
                { "value": pageName }
            ],
            "field_include_in_report": [
                { "value": true }
            ],
            "field_page_url": [
                {
                    uri: pageUrl,
                    options: [
                        //						{
                        //						  'fragment' : '#main-content',
                        //						}
                    ]
                }
            ],

            /** Comment out for now - it will become an image field  
            "field_automated_screeenshots": [

                {
                    "uri": imgdir + globalThis.screenshots[pageUrl]
                }

            ],
            */

            "field_abbreviation": [
                { "value": pageAbbrev }
            ],

            "field_document_links_on_page": drupalPdfList,

            "field_parent_audit_discovery": [
                { "target_id": this.auditNid }
            ],
            "type": [
                { "target_id": "discovered_page" }
            ]
        };

        console.log('About to call postNode');

        const nid = await this.postNode(payload);
        globalThis.currentPageDetails.nid = nid;

        console.log('Posted create, nid: ' + nid);

        globalThis.connector_status = 'Ready';

        return;

    }

    createDiscoveredPageIfNotExist(pageName, pageUrl, imgdir, pdfList) {

        // Check pageList agianst pageName amnd pageUrl 
        // We need both for header, footer etc.

        let exists = false;
        let abbrev = '';
        for (const pg of this.pageList) {

            if (pg.title === pageName && pg.field_page_url === pageUrl) {
                // exists
                exists = true;
                abbrev = pg.field_abbreviation_page;
                break;
            }
        }
        if (exists) {
            console.log('WARNING, page exists: ' + pageName + ' @ ' + pageUrl);
            return abbrev;
        }
        else {
            // Need to create it
            return this.createDiscoveredPage(pageName, pageUrl, imgdir, pdfList);
        }
    }

    async createFailurePoint(pageName, pageUrl, pageId, pageAbbrev, pointType, xpath, tmpId) {

        globalThis.connector_status = 'Busy';

        console.log('Creating failure point for ' + pageUrl + ", xpath: " + xpath);

        // Map from ARIA landmarks to faikure points for banner and contentinfo
        let pt = pointType;
        if (pointType === 'Banner') pt = 'Header';
        if (pointType === 'ContentInfo') pt = 'Footer';

        let found = false;
        let tid = '';
        for (const fpt of this.failurePointTypes) {
            console.log('testing: ' + fpt.name + ' against ' + pt)
            if (fpt.name === pt) {
                found = true;
                tid = fpt.tid;
                break;
            }
        }

        let fpName = this.auditAbbrev + '-' + pageAbbrev + '-' + pt + '-' + makeRnd(4);
        console.log('>>>> fpName: ' + fpName);
        console.log('tid: ' + tid);

        const payload = {
            "title": [
                { "value": fpName }
            ],
            "field_fp_temp_id": [
                { "value": tmpId }
            ],
            "field_xpath": [
                { "value": xpath }
            ],
            "field_parent_audit": [
                { "target_id": this.auditNid }
            ],
            "field_parent_discovered_page": [
                { "target_id": pageId }
            ],
            "field_failure_point": [
                { "target_id": tid, "target_type": "taxonomy_term" }
            ],
            "type": [
                { "target_id": "failure_point" }
            ]
        };

        console.log('About to post failure point')

        await this.postNode(payload);
        console.log('Posted failure point');

        globalThis.connector_status = 'Ready';

    }

    async getFailurePoints(pageId) {

        globalThis.connector_status = 'Busy';

        await this.getNodeSynchronous('rest/failure_points', 'pageId=' + pageId)
            .then(res => {
                console.log('got faulre points');
                console.log(res);
                globalThis.failurePointsList = res;
            });
        globalThis.connector_status = 'Ready';

    }

    async getIssueCategories(pageId) {

        globalThis.connector_status = 'Busy';

        await this.getNodeSynchronous('rest/issue_categories', '')
            .then(res => {
                console.log('got issue caegories');
                console.log(res);
                globalThis.issueCategories = res;
            });
        globalThis.connector_status = 'Ready';

    }

    async createIssue(pageId, tempFpId, xpath, issueCode, isWarn, cat) {

        globalThis.connector_status = 'Busy';

        console.log('Creating Issue ' + issueCode + ", xpath: " + xpath + "fpId: " + tempFpId);

        // Map the tempFpId to a nid
        let nid = null;
        for (const fp of globalThis.failurePointsList) {
            console.log(fp);
            console.log('Testing ' + fp.field_fp_temp_id)
            if (fp.field_fp_temp_id === tempFpId.toString()) {
                nid = fp.nid;
            }
        }
        console.log('Nid: ' + nid);

        const payload = {
            "title": [
                { "value": issueCode }
            ],
            /* Comment out for now so we don't need to deal with Workflow
            "field_ticket_status": [
                { "value": "ticket_status_fail" }
            ],
            */
            "field_xpath": [
                { "value": xpath }
            ],
            "field_parent_audit": [
                { "target_id": this.auditNid }
            ],
            "field_discovered_page_issue": [
                { "target_id": pageId }
            ],
            "field_parent_failure_point": [
                { "target_id": nid }
            ],
            "field_issue_category": [
                { "target_id": cat }
            ],
            /*** Comment out intile Susanna is finished 
            "field_created_by_automated_testi": [
                { "value": true }
            ],
            */
            "type": [
                { "target_id": "issue" }
            ]
        };

        console.log('About to post failure point')

        await this.postNode(payload);

        console.log('Posted Issue');

        globalThis.connector_status = 'Ready';

    }

    async createManualIssue(pageId, tempFpId, issueCode, transcript, screenshotUrl, timecode, videoId, note) {

        globalThis.connector_status = 'Busy';

        console.log('Creating Issue ' + issueCode);

        /* commented out for PROD (fields don't exist yet)

        // Get the failure points for current page
        await this.getFailurePoints(pageId);


        // Map the tempFpId to a nid
        let nid = null;
        for (const fp of globalThis.failurePointsList) {
            console.log(fp);
            console.log('Testing ' + fp.field_fp_temp_id)
            if (fp.field_fp_temp_id === tempFpId.toString()) {
                nid = fp.nid;
            }
        }
        console.log('Nid: ' + nid);
        */

        const formattedNote = '<h3>Transcript</h3>' + '<a href="' + screenshotUrl + '">Screenshot</a><pre>' + transcript + '</pre>';
        const formattedTranscript = '<h3>Transcript</h3>' + '<pre>' + transcript + '</pre>';

        const formattedBody = '<h3>What the issue is</h3><p>See video.</p><h3>Why this is important</h3><h3>Who it affects</h3><h3>How to remediate the issue</h3>';

        const payload = {
            "title": [
                { "value": issueCode }
            ],
            "body": [
                { "value": formattedBody }
            ],
            "field_ticket_status": [
                { "value": "ticket_status_fail" }
            ],
            /*
            "field_parent_audit": [
                { "target_id": this.auditNid }
            ], */
            "field_discovered_page_issue": [
                { "target_id": pageId }
            ],
            /* Commented out for PROD
            "field_parent_failure_point": [
                { "target_id": nid }
            ], 
            "field_created_by_automated_testi": [
                { "value": false }
            ], */
            "field_transcript": [
                { "value": formattedTranscript }
            ],
            "field_video_timecode": [
                { "value": timecode }
            ],
            "field_video": [
                { "target_id": videoId }
            ],
            "type": [
                { "target_id": "issue" }
            ],
            "field_issue_notes": [
                { "value": note }
            ],

        };

        console.log('About to post issue')

        await this.postNode(payload);

        console.log('Posted Issue');

        globalThis.connector_status = 'Ready';

    }

    async createTranscription(srcAudio, transcriptionnName, transcription) {

        globalThis.connector_status = 'Busy';

        console.log('Creating transcription ' + transcriptionnName + ", length: " + transcription.length);
        console.log('srcAudio: ' + srcAudio)
        const payload = {
            "title": [
                { "value": transcriptionnName }
            ],

            "field_parent_audit": [
                { "target_id": this.auditNid }
            ],

            "body": [
                { "value": transcription }
            ],

            "field_source_audio": [
                {
                    uri: srcAudio,
                    options: []
                }
            ],

            "type": [
                { "target_id": "transcript" }
            ]
        };

        console.log('About to post transcription')

        this.connectorResult = await this.postNode(payload);

        console.log('Posted Activity Report');

        globalThis.connector_status = 'Ready';

        return;

    }

    async createPromptResult(transcriptionId, goal, prompt, result) {

        console.log('Creating prompt result')

        globalThis.connector_status = 'Busy';

        console.log('Creating prompt result: ' + goal);

        const payload = {
            "title": [
                { "value": goal }
            ],
            "field_parent_transcription_id": [
                { "target_id": transcriptionId }
            ],

            "field_original_prompt": [
                { "value": prompt }
            ],

            "field_result_of_prompt": [
                { "value": result }
            ],

            "type": [
                { "target_id": "prompt_result" }
            ]
        };

        console.log('About to post prompt result')

        this.connectorResult = await this.postNode(payload);

        console.log('Posted prompt result');

        globalThis.connector_status = 'Ready';

        return this.connectorResult;

    }

    ///////

    async createAccessibilityConcern(title, concern) {

        console.log('Creating accessibility concern')

        globalThis.connector_status = 'Busy';

        const payload = {
            "title": [
                { "value": title }
            ],
            "field_audit": [
                { "target_id": this.auditNid }
            ],
            "body": [
                { "value": concern }
            ],
            "type": [
                { "target_id": "accessibility_concern" }
            ]
        };

        console.log('About to post accessibility concern')

        this.connectorResult = await this.postNode(payload);

        console.log('Posted accessibility concern');

        globalThis.connector_status = 'Ready';

        return this.connectorResult;

    }

    updateDiscoveredPages() {
        this.status = { ready: 'busy' };
        this.getNodeSynchronous('rest/discovered_pages', 'audit=' + this.auditNid)
            .then(res => {
                this.pageList = res;
                this.status = { ready: 'ready' };
            });
    }

    findPageIdByAbbrev(pageAbbrev) {
        let pageId = null;
        for (const pg in this.pageList) {
            console.log('Testing : ' + this.pageList[pg].field_abbreviation_page);
            if (this.pageList[pg].field_abbreviation_page === pageAbbrev) {
                // found created page
                console.log('!Found!');
                pageId = this.pageList[pg].nid;
                break;
            }
        }

        return pageId;

    }

    async getTranscription(transcriptionId) {

        globalThis.connector_status = 'Busy';
        this.connectorResult = await this.getNodeSynchronous('rest/get_transcript', 'transcriptId=' + transcriptionId);
        globalThis.connector_status = 'Ready';

    }

}


module.exports = {
    AlabsConnector: AlabsConnector,
    connector_init: AlabsConnector.connector_init,
    connector_get_status: AlabsConnector.get_status,
    connector_get_result: AlabsConnector.get_result,
    connector_create_failure_point: AlabsConnector.connector_create_failure_point,
    connector_update_discovered_pages: AlabsConnector.connector_update_discovered_pages,
    connector_find_pageId_by_abbrev: AlabsConnector.connector_find_pageId_by_abbrev,
}




//exports.createDiscoveredPage = createDiscoveredPage;


/*
const dummyPayload = {
    "title": [
      { "value": "This is a Discovered Page" }
    ],
    "field_plain_text": [
        { "value": 'hello' }
    ],
    "type": [
      { "target_id": "test_bob" }
    ]
};

//drupalConnection.postNode(dummyPayload);

*/