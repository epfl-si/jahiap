dcsl_data = {
    'properties': {
        'name': 'dcsl',
        'title': 'Data Center Systems Laboratory',
        'acronym': 'DCSL',
        'theme': 'ic',
        'breadcrumb_title': 'IC',
        'breadcrumb_url': 'http://ic.epfl.ch',
        'css_url': '//static.epfl.ch/v0.23.0/styles/ic-built.css'
    },
    'structure': {
        'boxes_per_pages': {
            "DCSL": 3,
            "Team": 9,
            "Publications": 1,
            "Teaching": 1,
            "soNUMA": 2,
            "IX Dataplane Operating System": 3,
        },
        'nb_files': 27
    },
    'sidebar': {
        'boxes': [
            {
                'title': "Competence or skills",
                'type': "coloredText",
                'content': "<p>We focus on interdisciplinary systems problems found in modern, large-scale datacenters. &nbsp; &nbsp;Our current research projects include specialized operating systems for datacenter applications, hardware support for software-defined networking, and energy-efficient, rack-scale computing.</p> <p>Key conferences : ASPLOS, ATC, ISCA, NSDI, SIGCOMM, SOCC, SOSP/OSDI.</p> <p>&nbsp;</p> ", # noqa
            }
        ]
    }
}

master_data = {
    'properties': {
        'name': 'master',
        'title': "MASTER'S STUDIES",
        'acronym': 'EPFL',
        'theme': 'epfl',
        'breadcrumb_title': 'Prospective students',
        'breadcrumb_url': 'http://futuretudiant.epfl.ch/',
        'css_url': '//static.epfl.ch/v0.23.0/styles/epfl-built.css'
    },
    'structure': {
        'boxes_per_pages': {
            'Master': 1,
            'Why choose EPFL?': 2,
            'International Rankings': 1,
            'Fairs calendar': 4,
            'Meet our students': 1,
            "Master's Programs": 1,
            'Specialized Masters Day': 3,
            'Programs Overview': 1,
            'Minors and Specializations': 1,
            'Applied Mathematics': 1,
            'Architecture': 2,
            'Bioengineering': 2,
            'Data Science': 2,
            'Chemical Engineering and Biotechnology': 2,
            'Civil Engineering': 2,
            'Communication Systems': 2,
            'Computational Science and Engineering': 2,
            'Computer Science': 2,
            'Digital Humanities': 2,
            'Electrical and Electronic Engineering': 2,
            'Energy Management and Sustainability': 2,
            'Environmental Sciences and Engineering': 2,
            'Financial Engineering': 2,
            'Life Sciences and Technology': 2,
            'Management, technology and entrepreneurship': 2,
            'Materials Science and Engineering': 2,
            'Mathematics': 2,
            'Mathematics for education (in French only)': 1,
            'Mechanical Engineering': 2,
            'Microengineering': 2,
            'Molecular and Biological Chemistry': 2,
            'Nuclear Engineering': 2,
            'Physics and Applied Physics': 2,
            'Double Diplomas and Joint Degrees': 1,
            "1:1 Master's EPFL-DTU": 2,
            'Double diploma EPFL-Polytechnique Montréal': 2,
            'Double Diploma EPFL-Centrale Lille': 2,
            'ENS de Lyon Informatique et Syscom': 2,
            'Admission Criteria & Application': 2,
            'Online application': 2,
            'Tuition Fees & Excellence Fellowships': 1,
            'Excellence Fellowships': 1,
            'Practical Info & Useful Links': 1,
            'Coming from abroad': 1,
            'Teaching Languages': 1,
            'FAQ': 1,
        },
        'nb_files': 171
    },
    'sidebar': {
        'boxes': [
            {
                'title': "Application",
                'type': "coloredText",
                'content': '<p><strong><a href="https://isa.epfl.ch/imoniteur_ISAP/!farforms.htm?x=master">Applications</a> for starting a Master\'s program are open from mid-November to January 15th and from January 16th to April 15th</strong></p> ', # noqa
            },
            {
                'title': "Contact",
                'type': "text",
                'content': '<p style="text-align: left;">In case of questions, please contact the student helpdesk:</p> <div class="button mail"><a href="mailto:student.services@epfl.ch"> <button class="icon"></button> <span class="label">student.services@epfl.ch</span></a></div> <p>&nbsp;</p> <div class="button contact"><button class="icon"></button> <span class="label">+41 (0)21 693 43 45</span></div> ', # noqa
            },
            {
                'title': "Discover the campus",
                'type': "text",
                'content': '<p><a href="http://virtualtour.epfl.ch" target="_blank"><img width="300" height="157" src="/files/buttons/virtual tour thumbnail.png?uuid=default:1ecf5f72-58c7-40f6-a15d-5ca0ffd2c419" alt="virtual tour" /></a></p> ', # noqa
            },
            {
                'title': "FOLLOW EPFL",
                'type': "text",
                'content': '<p style="text-align: left;"><a target="_blank" href="http://www.youtube.com/EPFLstudents"><img width="25" height="25" alt="EPFL on YouTube" src="/files/buttons/YouTube-social-square_red_48px.png?uuid=default:f9ad6a38-48ec-4629-befe-080249712f3d" /></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a target="_blank" href="http://www.facebook.com/EPFL.ch"><img width="25" height="25" alt="EPFL on Facebook" src="/files/buttons/FB-f-Logo__blue_58.png?uuid=default:187bafe8-c769-4aee-879b-7d2920600f30" /></a>&nbsp; &nbsp; &nbsp; <a target="_blank" href="http://twitter.com/EPFL_en"><img width="25" height="21" alt="EPFL on Twitter" src="/files/buttons/Twitter_logo_blue.png?uuid=default:7b12cfa6-30f8-4d08-9849-1096739f5eb2" /></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a target="_blank" href="https://instagram.com/epflcampus/"><img width="25" height="25" alt="EPFL on Instagram" src="/files/buttons/insta_logo.jpg?uuid=default:8002075d-fb77-46dd-bdaf-79cd4855a818" /></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a target="_blank" href="http://studyingatepfl.tumblr.com/"><img width="25" height="25" alt="tumblr" src="/files/buttons/tumblr.png?uuid=default:073896a0-c6cd-46cb-82ce-342f5d293110" /></a></p> ' # noqa
            },
        ]
    }
}


def get_sites():
    return [
        'master',
        'dcsl',

    ]
