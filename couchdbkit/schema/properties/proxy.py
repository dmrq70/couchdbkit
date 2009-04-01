# -*- coding: utf-8 -*-
# Copyright 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import couchdbkit
from couchdbkit.schema.properties import Property
from couchdbkit.schema.base import DocumentSchema
from couchdbkit.schema.exceptions import *

__all__ = ['SchemaProperty']

class SchemaProperty(Property):
    """ Schema property. It allow you add a DocumentSchema instance 
    a member of a Document object. It return a
    :class:`simplecouchdb.schemaDocumentSchema` object.

    Exemple :
    
        >>> from simplecouchdb.schema import *
        >>> class Blog(DocumentSchema):
        ...     title = StringProperty()
        ...     author = StringProperty(default="me")
        ... 
        >>> class Entry(Document):
        ...     title = StringProperty()
        ...     body = StringProperty()
        ...     blog = SchemaProperty(Blog())
        ... 
        >>> test = Entry()
        >>> test._doc
        {'body': None, 'doc_type': 'Entry', 'title': None, 'blog': {'doc_type': 'Blog', 'author': u'me', 'title': None}}
        >>> test.blog.title = "Mon Blog"
        >>> test._doc
        {'body': None, 'doc_type': 'Entry', 'title': None, 'blog': {'doc_type': 'Blog', 'author': u'me', 'title': u'Mon Blog'}}
        >>> test.blog.title
        u'Mon Blog'
        >>> from simplecouchdb import Server
        >>> s = Server()
        >>> db = s.create_db('simplecouchdb_test')
        >>> Entry._db = db 
        >>> test.save()
        >>> doc = Entry.objects.get(test.id)
        >>> doc.blog.title
        u'Mon Blog'
        >>> del s['simplecouchdb_test']

    """

    def __init__(self, schema, verbose_name=None, name=None, 
            required=False, validators=None, default=None):

        Property.__init__(self, verbose_name=None,
            name=None, required=False, validators=None)
       
        use_instance = True
        if type(schema) == simplecouchdb.schema.base.DocumentSchemaBase:
            use_instance = False    

        elif not isinstance(schema, DocumentSchema):
            raise TypeError('schema should be a DocumentSchema instance')
       
        elif schema.__class__.__name__ == 'DocumentSchema':
            use_instance = False
            properties = schema._dynamic_properties.copy()
            schema = DocumentSchema.build(**properties)
            
        self._use_instance = use_instance
        self._schema = schema
        
    def default_value(self):
        if not self._use_instance:
            return self._schema()
        return self._schema.clone()

    def empty(self, value):
        if not hasattr(value, '_doc'):
            return True
        if not value._doc or value._doc is None:
            return True
        return False

    def validate(self, value, required=True):
        value.validate(required=required)
        value = super(SchemaProperty, self).validate(value)

        if value is None:
            return Value

        if not isinstance(value, DocumentSchema):
            raise BadValueError(
                'Property %s must be DocumentSchema instance, not a %s' % (self.name, 
                type(value).__name__))
        
        return value

    def _to_python(self, value):
        if not self._use_instance: 
            schema = self._schema()
        else:
            schema = self._schema.clone()
        return schema.wrap(value)

    def _to_json(self, value):
        if not isinstance(value, DocumentSchema):
            if not self._use_instance:
                schema = self._schema()
            else:
                schema = self._schema.clone()

            if not isinstance(value, dict):
                raise BadValueError("%s is not a dict" % str(value))
            value = schema(**value)
        return value._doc
