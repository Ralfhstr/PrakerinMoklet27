# -*- coding: utf-8 -*-
import json
from odoo import http, _,exceptions 
from odoo.http import request
import time
import locale

from pusher import Pusher

# configure pusher object
pusher = Pusher(
app_id='1019595',
key='ec0971857e980f699709',
secret='d4a647edb00e85d10eed',
cluster='ap1',
ssl=True)

class Erups(http.Controller):

    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
    
    def __init__(self):
        self._model_erups = "erups"
        self._model_erups_agenda = "erups_agenda"
        self._model_erups_question = "erups_question"
        
    # @http.route('/message',type='http', auth='public', methods=['GET'])
    # def message(self, **params):
    #     #data = request.form
    #     pusher.trigger(u'message', u'send', {
    #         u'name': 'viki',
    #         u'message': 'hallo'
    #     })
    #     return "message sent"
        
    @http.route('''/''',type='http', auth='public', website=True)
    def home(self, **params):
        url = '/login/'
        return http.request.redirect(url)
        
    @http.route('''/admin''',type='http', auth='public', website=True)
    def admin(self, **params):
        url = '/web/login'
        return http.request.redirect(url)

    @http.route('''/register/''',type='http', auth='public', website=True)
    def register(self, **params):
        return request.render("erups_question.register", {})

    @http.route('''/''',type='http',auth='public', website=True)
    def login(self, **params):
        return request.render("erups_question.login", {})
    
    @http.route('''/pertanyaan''',type='http', auth='public', website=True)
    def admin(self, **params):
        url = '/formpertanyaan'
        return http.request.redirect(url)

    @http.route(['''/formpertanyaan''', '''/formpertanyaan/<int:erups_id>'''], auth='public', website=True)
    def index(self, erups_id=None, **params):
        
        sql2 = "SELECT * FROM erups_question eq LEFT JOIN erups_agenda ea ON ea.id = eq.agenda_id WHERE ea.status = 'open';"
        request.env[self._model_erups_question].sudo()._cr.execute(sql2)
        questioncheck = request.cr.fetchall()
        
        sql3 = "SELECT * FROM erups_agenda WHERE status = 'open';"
        request.env[self._model_erups_question].sudo()._cr.execute(sql3)
        agendacheck = request.cr.fetchall()
        
        if erups_id == None:
            erups = http.request.env[self._model_erups].sudo().search([])
            values = {
                "erups": erups,
                "message": len(agendacheck),
            }
            print(erups)
            return http.request.render('erups_question.erups', values)
        else:
            sql1 = "SELECT * FROM erups WHERE id = '%s';" % (erups_id)
            request.env[self._model_erups_question].sudo()._cr.execute(sql1)
            res = request.cr.fetchall()
            if len(res) > 0:
                erups = http.request.env[self._model_erups].sudo().search(
                    [('id', '=', erups_id)])
                agenda = http.request.env[self._model_erups_agenda].sudo().search(
                    [('erups_id', '=', erups_id),('status', '=', 'open')],order='id asc')
                
                if erups.status == 'close':
                    url = '/formpertanyaan/'
                    return http.request.redirect(url)
                else:
                    values = {
                        "erups": erups,
                        "agenda": agenda,
                        "message": len(questioncheck),
                    }
                    print(erups)
                    return http.request.render('erups_question.form_question', values)
            else:
                values = {
                    "message":  'Kegiatan tidak ditemukan',
                }
                return http.request.render('erups_question.pagenotfound',values)

    @http.route(['/formpertanyaan/save'], type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def rups_save(self, **post):

        rups_id = post['rups_id']
        
        data = {
            "registration_number": post['registration_number'],
            "email": post['email'],
            "name": post['name'],
            "authority_holder": post['authority_holder'],
            "share_count": post['share_count'],
            "agenda_id": post['agenda_id'],
            # "agenda_id": '2',
            "question": post['question'],
        }
        
        # filter_ar = [
        #     ('registration_number', '=', post['registration_number']),
        #     ('agenda_id', '=', post['agenda_id']),
        # ]
        # records = request.env[self._model_erups_question].sudo().search_count(filter_ar)
        sql1 = "SELECT * FROM erups_question WHERE registration_number = '%s' AND agenda_id = '%s';" % (data['registration_number'],data['agenda_id'])
        request.env[self._model_erups_question].sudo()._cr.execute(sql1)
        res_one = request.cr.fetchall()
         #json.dumps(res_one)
        sql2 = "SELECT * FROM erups_question WHERE agenda_id = '%s';" % (data['agenda_id'])
        request.env[self._model_erups_question].sudo()._cr.execute(sql2)
        questioncheck = request.cr.fetchall()
        
        sql3 = "SELECT * FROM erups_agenda WHERE id = '%s' AND status = '%s' ;" % (data['agenda_id'],'open')
        request.env[self._model_erups_question].sudo()._cr.execute(sql3)
        agendacheck = request.cr.fetchall()
        
        if len(questioncheck) >= 10:
            values = {
                "message":  'Jumlah Penanya sudah mencapai batas sebanyak 10 (sepuluh) Penanya per sesi',
            }
            return http.request.render('erups_question.messagepage',values)
        else:
            # if len(res_one) > 0:
            #     values = {
            #         "message":  'Pemegang Saham hanya bisa mengajukan Satu Pertanyaan per Agenda',
            #     }
            #     return http.request.render('erups_question.warningpage',values)
            #     # raise exceptions.ValidationError(
            #     #     "Pemegang Saham hanya bisa mengajukan Satu Pertanyaan per Agenda"
            #     # )
            # else:
            if len(agendacheck) > 0:
                rec_save = request.env[self._model_erups_question].sudo().create(data)
                if rec_save:
                    #return http.request.render('erups_question.terimakasih')
                    url = '/thankyou/'
                    return http.request.redirect(url)
                else:
                    values = {
                        "message":  'Maaf, Gagal Menyimpan Data'
                    }
                    return http.request.render('erups_question.warningpage',values)
            else:
                values = {
                    "message":  'Agenda telah ditutup / Agenda telah selesai',
                }
                return http.request.render('erups_question.messagepage',values)

    @http.route('/thankyou', auth='public', methods=['GET'], website=True)
    def thankyou(self, **params):

        sql2 = "SELECT * FROM erups_question eq LEFT JOIN erups_agenda ea ON ea.id = eq.agenda_id WHERE ea.status = 'open';"
        request.env[self._model_erups_question].sudo()._cr.execute(sql2)
        questioncheck = request.cr.fetchall()
        
        #data = request.form
        pusher.trigger(u'message', u'send', {
            u'name': 'viki',
            u'message': len(questioncheck)
        })
        
        values = {
            'base_url': 'terimakasih telah mengisi pertanyaan',
        }
        return http.request.render('erups_question.terimakasih', values)

    @http.route('/viki', auth='public', methods=['GET'], website=True)
    def viki(self, **params):

        data = {
            # "rups_id": post['rups_id'],
            "registration_number": '123',
            "email": 'viki@email.com',
            "name": 'viki',
            "authority_holder": 'awds',
            "share_count": '10',
            "agenda_id": '2',
            # "agenda_id": '2',
            "question": '??',
        }
        
        sql = "SELECT * FROM erups_question WHERE registration_number = '%s' AND agenda_id = '%s';" % (data['registration_number'],data['agenda_id'])
        request.env[self._model_erups_question].sudo()._cr.execute(sql)
        res_one = request.cr.fetchall()
        #fetchone() will return the first element found as dictionary
        
        total_len = request.env[self._model_erups_question].browse([('registration_number', '=', '123'),('agenda_id', '=', '2')])
        
        filter_ar = [
            ['registration_number', '=', '123'],
            ['agenda_id', '=', '2']
        ]
        records = request.env[self._model_erups_question]
        records = records.sudo().search_count(filter_ar)
        
        #json.dumps(total_len)
        # if records > 0:
        #     values = {
        #         "message":  'Pemegang Saham hanya bisa mengajukan Satu Pertanyaan per Agenda',
        #     }
        #     return http.request.render('erups_question.erups',values)
        # else:
        #     res = request.env[self._model_erups_question].sudo().create(data)
        return http.Response(
            json.dumps(time.strftime("%a, %d %b %Y %H:%M:%S")),
            status=200,
            mimetype='application/json'
        )
            # if res:
            #     return http.request.render('erups_question.terimakasih')
            # else:
            #     values = {
            #         "message":  'Maaf, Gagal Menyimpan Data'
            #     }
            #     return http.request.render('erups_question.erups',values)

# class Erups_form_question(http.Controller):

#     def __init__(self):
#         self._model_erups = "erups"
#         self._model_erups_agenda = "erups_agenda"

#     @http.route('/formpertanyaan/<int:erups_id>', auth='public', website=True)
#     def index(self, erups_id=None, **params):

#         erups = http.request.env[self._model_erups].sudo().search(
#             [('id', '=', erups_id)])
#         agenda = http.request.env[self._model_erups_agenda].sudo().search(
#             [('erups_id', '=', erups_id)])
#         values = {
#             "erups": erups,
#             "agenda": agenda,
#         }
#         print(erups)
#         return http.request.render('erups_question.form_question', values)

#     @http.route('/erups_question/erups_question/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('erups_question.listing', {
#             'root': '/erups_question/erups_question',
#             'objects': http.request.env['erups_question.erups_question'].search([]),
#         })

#     @http.route('/erups_question/erups_question/objects/<model("erups_question.erups_question"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('erups_question.object', {
#             'object': obj
#         })
