from flask import jsonify, g, request, url_for
from app import db
from app.bucketlist_api_v1 import blist_api
# from .. import db
from app.auth import auth_token
from app.models import Bucketlist
from datetime import datetime
# from bucketlist_api_v1.errors import .


@blist_api.route('/', methods=['GET'])
@blist_api.route('/bucketlists/', methods=['GET', 'POST'])
@auth_token.login_required
def bucketlists():
    if request.method == 'GET':
        # implementation for viewing all bucketlists
        bucket = Bucketlist.query.filter_by(owner=g.user.id)
        if not bool(bucket.all()):
            return jsonify({'message': 'You have not added any bucketlist yet'}), 200
        page = 1 if not request.args.get(
            'page') else int(request.args.get('page'))

        if not request.args.get('limit'):
            limit = 20
        if request.args.get('limit'):
            limit = int(request.args.get('limit')) if int(
                request.args.get('limit')) < 100 else 100

        q = request.args.get('q')
        if q:
            # bucket.filter(Bucketlist.name.contains(q))
            paged_bucket = bucket.filter(Bucketlist.name.contains(
                '%' + q + '%')).paginate(page, limit, False)
        else:
            paged_bucket = bucket.paginate(page, limit, True)
        return jsonify({"Bucketlists": [{"name": bucketlist.name,
                                         "Date Added": bucketlist.created,
                                         "Date Modified": "Not applicable" if bucketlist.modified == bucketlist.created else bucketlist.modified,
                                         "Created by": bucketlist.owner,
                                         "ID": bucketlist.id
                                         } for bucketlist in paged_bucket.items] if len(paged_bucket.items) > 0 else "No bucketlists to display",
                        "Previous Page": paged_bucket.prev_num if paged_bucket.has_prev else "No previous bucketlists",
                        "Next Page": paged_bucket.next_num if paged_bucket.has_next else "No more bucketlists to view"
                        }), 200

    else:
        # implementation for creating a bucketlist
        
        blist = Bucketlist()
        blist.import_data(request.json)
        if Bucketlist.query.filter_by(name=blist.name).first():
            return jsonify({"message": "Bucketlist '{}' already exists".format(blist.name)}), 409
        if not blist.name:
            return jsonify({"message": "Bucketlist name is required"}), 400
        else:
            if str(blist.name).isdigit():
                return jsonify({"message": "Bucketlist name can not have just numbers"}), 400
            db.session.add(blist)
            db.session.commit()
            data = {
                "Bucketlist Name": blist.name,
                "Date Added": blist.created}
            return jsonify({'Successfully Created Bucketlist with details': data}), 201


@blist_api.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth_token.login_required
def single_bucketlist(id):
    if request.method == 'GET':
        # implementation for viewing a single bucketlist
        bucketlist = Bucketlist.query.get_or_404(id)
        if bucketlist.owner != g.user.id:
            return jsonify({'message': 'You are not authorised to view this bucketlist!'}), 401
        # bucketlist = Bucketlist.query.get_or_404(id)
        FMT = '%Y-%m-%d %H:%M:%S.%f'
        time_diff = datetime.strptime(
            str(bucketlist.modified), FMT) - datetime.strptime(str(bucketlist.created), FMT)
        if int(time_diff.total_seconds()) < 1:
            modified = "Not Applicable. This bucketlist has not yet been modified"
        else:
            modified = bucketlist.modified
        bucketlist_items = [item.name for item in bucketlist.items.all()]
        data = {
            "Bucketlist Name": bucketlist.name,
            "Bucketlist Items": bucketlist_items if bucketlist_items else str(bucketlist.name) + " has no items",
            "Date Added": bucketlist.created,
            "Date Modified": modified,
            "Created by": bucketlist.owner,
            "ID": bucketlist.id
        }

        return jsonify({'Bucketlist Details': data}), 200
    elif request.method == 'PUT':
        # implementation for updating a single bucketlist
        bucketlist = Bucketlist.query.get_or_404(id)
        if bucketlist.owner != g.user.id:
            return jsonify({'message': 'You are not authorised to modify this bucketlist!'}), 401
        bucketlist.import_data(request.json)
        if Bucketlist.query.filter_by(name=bucketlist.name).first():
            return jsonify({"message": "Bucketlist '{}' already exists".format(bucketlist.name)}), 409
        db.session.commit()
        return jsonify({'Successfully Updated Bucketlist with details':
                        [{
                            "Bucketlist Name": bucketlist.name,
                            "Date Added": bucketlist.created,
                            "Date Modified": bucketlist.modified
                        }
                        ]
                        }), 202

    else:
        # deleting a bucketlist
        bucketlist = Bucketlist.query.get_or_404(id)
        if bucketlist.owner != g.user.id:
            return jsonify({'message': 'You are not authorised to delete this bucketlist!'}), 401
        db.session.delete(bucketlist)
        db.session.commit()
        return jsonify({'message': 'Bucketlist successfully deleted'}), 200


