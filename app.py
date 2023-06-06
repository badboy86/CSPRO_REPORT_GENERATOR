import os
from flask import Flask, render_template, request, send_file, Response
import werkzeug
from werkzeug.utils import secure_filename
from pycspro import DictionaryParser
import json
import logging
import shutil
import datetime
from io import BytesIO
import zipfile




logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__, static_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'dcf'}
@app.errorhandler(404)
def not_found_error(error):
    # Log the error
    app.logger.error('Page not found: %s', request.path)

    # Return a custom error page or JSON response
    return render_template('error.html', error_message='Page not found'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])

def upload_file():
    if request.method == 'POST':
        # Vérifier si un fichier a été envoyé
        if 'file' not in request.files:
            return 'Aucun fichier sélectionné.'
        
        file = request.files['file']
        
        # Vérifier si le nom de fichier est vide
        if file.filename == '':
            return 'Aucun fichier sélectionné.'
        
        # Vérifier si le fichier est autorisé
        if not allowed_file(file.filename):
            return 'Type de fichier non autorisé.'
        
        # Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            # Enregistrer le fichier sur le serveur
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Exécuter le code pour générer le rapport
            generate_report(filename,timestamp)
            
            # Supprimer le fichier téléchargé après avoir généré le rapport
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Télécharger automatiquement le fichier de rapport
            #return send_file('report1.html', as_attachment=True)
            # Spécifiez le nom de l'archive zip que vous souhaitez créer
            # Générer un nom de fichier unique avec un horodatage

            zip_filename = f'report_{timestamp}.zip'
            files_to_compress = [
                f'report_{timestamp}.html',
                'wwwroot',
            ]

                # Créer un flux de données en mémoire
            zip_data = BytesIO()

            # Créer l'archive zip en utilisant le flux de données en mémoire
            with zipfile.ZipFile(zip_data, 'w') as zip_file:
                for item in files_to_compress:
                    if os.path.isfile(item):
                        zip_file.write(item, os.path.basename(item))
                    elif os.path.isdir(item):
                        for root, _, files in os.walk(item):
                            for file in files:
                                file_path = os.path.join(root, file)
                                zip_file.write(file_path, os.path.relpath(file_path, item))

            # Définir les en-têtes de la réponse pour spécifier le type de contenu et le nom du fichier
            headers = {
                'Content-Type': 'application/zip',
                'Content-Disposition': f'attachment; filename="{zip_filename}"'
            }
            os.remove( f'report_{timestamp}.html')
            # Revenir au début du flux de données
            zip_data.seek(0)

            # Envoyer le fichier zip en tant que réponse avec les en-têtes appropriés
            return Response(zip_data, headers=headers)
        
        except Exception as e:
            # En cas d'erreur, libérer le fichier et afficher le message d'erreur
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f'Erreur lors de la génération du rapport : {str(e)}'
    
    return render_template('index.html')

def generate_report(filename,timestamp):
    try:
        # Code pour générer le rapport à partir du fichier
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r', encoding='utf-8') as f:
            raw_dictionary = f.read()
            
        # Code pour parser et manipuler les données du fichier
        dictionary_parser = DictionaryParser(raw_dictionary)
        parsed_dictionary = dictionary_parser.parse()
        #parsed_dictionary=json.dumps(parsed_dictionary, indent=4).encode('latin-1').decode('unicode_escape')
        parsed_dictionary=json.dumps(parsed_dictionary,ensure_ascii=False, indent=4)

        #parse json str to dictionary python
        dictData= json.loads(parsed_dictionary)

        html_content=generate_html_content(dictData['Dictionary']['Name'],dictData['Dictionary']['Level'])
        # Code pour générer le contenu HTML du rapport
        
        # Code pour enregistrer le rapport généré
        with open(f'report_{timestamp}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    except Exception as e:
        raise e

def datatype(element):
    if element['DataType'] == "Alpha":
        if 'ValueSets' in element.keys():
            return r"%l"
        return r"%s"
    if element['DataType']== "Numeric":
        return r"%v"
    return r"%s"
    
def generate_header_html(dictName):
    return '''
    <!doctype html>
<html>
<head>

    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no, minimum-scale=1">
    <link rel="stylesheet" href="./css/bootstrap.min.css" />
    <link rel="stylesheet" href="./css/bootstrap-icons.css" />
    <link rel="stylesheet" href="./css/adminlte.min.css" />
    <link rel="stylesheet" href="./css/all.min.css" />
    <link rel="stylesheet" href="./css/rep.css" />

    <script src="./js/jquery.min.js"></script>
    <script src="./js/bootstrap.bundle.min.js"></script>
    <script src="./js/adminlte.min.js"></script>    
    <script src="./js/rep.js"></script>
    
    <!-- Report properties-->
  <? setlanguage("AR");
  loadcase({0},gKey);
  ?>
    <title>Rapport</title>
</head>
<body>
    <div class="content">
        <div class="container">
            
                <div class="mt-2" style="text-align: right;">
                    <a id="aCollapse" style="cursor:pointer;" data-toggle="tooltip" data-placement="top" title="DEVELOPPER/REDUIRE">
                        <i class="fa fa-plus"></i> <span class="ml-1">
                            DEVELOPPER/REDUIRE
                        </span>
                    </a>
                </div>
               
            </div>
            <div class="mt-3" id="div-1">
    '''.format(dictName)

def footer_html():
    return '''
    
    <footer class="page-footer font-small bg-dark">
        <div class="footer-copyright text-center text-light py-3">
            RAPPORT GENEREE LE:  ~~timestring("%H:%M - %m/%d/%y")~~
        </div>
    </footer>

</body>

</html>
    '''

def generate_html_div_module_multi(dictName,moduleDict):
    # Define the HTML template string
    template = '''
        <div id="{5}">
            <div class="card card-light shadow ">
                <div class="card-header" data-card-widget="collapse" style="cursor:pointer;">
                    <h3 class="card-title text-bold">
                         ~~getlabel({0})~~
                    </h3>
                    <div class="card-tools">
                        <button type="button" class="btn btn-tool" data-card-widget="collapse">
                            <i class="fas fa-minus"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body" style="overflow-x:auto;">
                    <table class="table table-striped table-bordered" style="direction:rtl;text-align:right;  width: 100%; margin: 0 auto;">
                        <thead class="thead-dark">
                            <tr>
                                {1}
                            </tr>
                        </thead>
                        <tbody>
                            <? do numeric ctr = 1 while ctr <= count({2}.{3}) ?>
                            <tr>
                                {4}
                            </tr>
                            <? enddo; ?>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    '''

    # Define the title of module
    
        # Define the column headers using the given variable names
    headers = '\n'.join(['<th>~~getlabel({0})~~</th>'.format(dictName+'.'+var['Name']) for var in moduleDict['Items']])
    

    # Define the row cells using the given variable names and a loop counter
    cells = '\n'.join(['<td>~~maketext("{0}", {1}(ctr))~~</td>'.format(datatype(var),dictName+'.'+var['Name'])
                       for var in moduleDict['Items'] ])


    # Combine the headers and cells to create the final HTML code
    html = template.format(dictName+'.'+moduleDict['Name'],headers,dictName,moduleDict['Name'], cells,dictName+'.'+moduleDict['Name'])

    return html

def  generate_html_div_module_mono(dictName,moduleDict):
    # Define the HTML template string
    template = '''
  <div id="{0}" style="direction:rtl;">
                    <div class="card card-light shadow ">
                        <div class="card-header" data-card-widget="collapse" style="cursor:pointer;">
                            <h3 class="card-title text-bold">
                                ~~getlabel({1})~~
                            </h3>
                            <div class="card-tools">
                                <button type="button" class="btn btn-tool" data-card-widget="collapse">
                                    <i class="fas fa-minus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="card-body" style="overflow-x:auto;">
                            {2}
                        </div>
                    </div>
                </div>
   '''
    cells = '\n'.join(['<dt>~~getlabel({0})~~</dt><dd>~~maketext("{1}", {2})~~</dd>'.format(dictName+'.'+var['Name'],datatype(var),dictName+'.'+var['Name'])
                       for var in moduleDict['Items'] ])

    html = template.format(dictName+'.'+moduleDict['Name'],dictName+'.'+moduleDict['Name'], cells)
    return html

def  generate_html_div_module_IdItem(dictName,moduleDict):
    # Define the HTML template string
    template = '''
  <div id="Iditem" style="direction:rtl;">
                    <div class="card card-light shadow ">
                        <div class="card-header" data-card-widget="collapse" style="cursor:pointer;">
                            <h3 class="card-title text-bold">
                               Identification
                            </h3>
                            <div class="card-tools">
                                <button type="button" class="btn btn-tool" data-card-widget="collapse">
                                    <i class="fas fa-minus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="card-body" style="overflow-x:auto;">
                            <div class="row mb-3">
                                <div class="col-3">
                                    {0}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
   '''
    cells = '\n'.join(['<dt>~~getlabel({0})~~</dt><dd>~~maketext("{1}", {2})~~</dd>'.format(dictName+'.'+var['Name'],datatype(var),dictName+'.'+var['Name'])
                       for var in moduleDict])
    html = template.format(cells)
    return html

def generate_html_content(dictName,moduleDict):
    content = generate_header_html(dictName)+ generate_html_div_module_IdItem(dictName,moduleDict['IdItems']) 
    for module in moduleDict['Records']:
        if(module['MaxRecords']==1):
            content = content + generate_html_div_module_mono(dictName,module)
        else:
            content = content + generate_html_div_module_multi(dictName,module)
    content = content + footer_html()
    return content



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)