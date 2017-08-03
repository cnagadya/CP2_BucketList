"""Functionality for adding, updating and deleting items within a bucketlist"""

from flask import jsonify, request, g
from app import db
from . import blist_api
from datetime import datetime
# from .. import db
from app.auth import auth_token
from app.models import Item, Bucketlist


@blist_api.route('/bucketlists/<int:id>/items/', methods=['POST'])
@auth_token.login_required
def add_item(id):
    bucketlist = Bucketlist.query.get_or_404(id)
    if bucketlist.owner != g.user.id:
        return jsonify({
            'message': "You have no access to this bucketlist"
        }), 401
    item = Item()
    item.import_data(request.json, bucketlist.id)
    if not item.name or str(item.name).isspace():
        return jsonify({"message": "Item name is required"}), 400
    if item.done and item.done not in (0, 1):
        return jsonify({
            "message": "Done can only either be '1' for True or '0' for False"
        }), 400
    bucketlist.modified = datetime.now()
    db.session.add(item)
    db.session.commit()
    # implementation for adding an item to a bucketlist
    return jsonify({'Successfully Added item with details':
                    [{"Item name": item.name,
                      "Item ID": item.id,
                      "Added to": bucketlist.name
                      }]
                    }), 201


@blist_api.route('/bucketlists/<int:id>/items/<int:item_id>',
                 methods=['PUT', 'DELETE'])
@auth_token.login_required
def modify_item(id, item_id):
    if request.method == 'PUT':

        bucketlist = Bucketlist.query.get_or_404(id)
        if bucketlist.owner != g.user.id:
            return jsonify({
                'message': "You have no access to this bucketlist"
            }), 401
        item = Item.query.filter_by(list_id=id, id=item_id).first()
        if item:
            if item.import_data(request.json, bucketlist.id) == "error":
                return jsonify({
                    "message": "At least item 'name' or 'Done' is required"
                }), 400
            else:
                if item.import_data(request.json, bucketlist.id) == "blank":
                    return jsonify({"message": "Invalid item name"}), 400
                elif item.done not in (0, 1):
                    return jsonify({
                        "message":
                        "Done can only either be '1' for True or '0' for False"
                    }), 400
                else:
                    bucketlist.modified = datetime.now()
                    db.session.commit()
                    # implementation for editing a bucketlist item
                    return jsonify({'Successfully Changed to':
                                    [{"Item name": item.name,
                                      "Item ID": item.id,
                                      "Done": item.done
                                      }]}), 201
        else:
            return jsonify({
                "message": "Invalid bucketlist or item id "}), 404
    else:
        # implementation for deleting an item from a bucketlist
        bucketlist = Bucketlist.query.filter_by(id=id, owner=g.user.id).first()
        item = Item.query.filter_by(list_id=bucketlist.id, id=item_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({
                'message': 'Item successfully deleted from ' + bucketlist.name
            }), 410
        else:
            return jsonify({
                "message": bucketlist.name + " contains no item with id " +
                str(item_id)}), 404
