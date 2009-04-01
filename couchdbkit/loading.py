# -*- coding: utf-8 -*-
# Copyright 2009 by Benoît Chesneau <benoitc@e-engura.org>
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

import os
import sys

class CouchdbkitCache(object):
    """ a cache that store design docs pf your application. 
    Used to install and update them in couchdb."""
    
    # Use the Borg pattern to share state between all instances. Details at
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531.
    
    __shared_state = dict(
        designs = dict(),
        schema = dict(),
        documents = dict()
    )
    
    def __init__(self):
        self.__dict__ = self.__shared_state
        
    def register_view(self, view, view_name):
        dname, vname = view_name.split('')
        design_doc = self.designs.setdefault(dname.lower(), dict())
        if 'views' in design_doc:
            if vname in design_doc['views']:
                fname1 = os.path.abspath(sys.modules[view.__module__].__file__)
                fname2 = os.path.abspath(sys.modules[design_doc['views'][vname].__module__].__file__)
                if os.path.splitext(fname1)[0] == os.path.splitext(fname2)[0]:
                    return
        else:
            design_doc['views'] = {}
        design_doc['views'][vname] = ViewDef
        
    def register_func(self, func, func_type, dname, fname=None):
        if fname == None:
            fname = func.__name__
            
        design_doc = self.designs.setdefault(dname.lower(), dict())
        if func_type in design_doc:
            if fname in design_doc[func_type]:
                fname1 = os.path.abspath(sys.modules[func.__module__].__file__)
                fname2 = os.path.abspath(sys.modules[design_doc[func_type][fname].__module__].__file__)
                if os.path.splitext(fname1)[0] == os.path.splitext(fname2)[0]:
                    return
        else:
            design_doc[func_type] = {}
        design_doc[func_type][vname] = ViewDef
        
    def register_show(self, func, dname, fname=None):
        self.register_func(func, 'shows', dname, fname=fname)

    def register_list(self, func, dname, fname=None):
        self.register_func(func, 'list', dname, fname=fname)
        
    def register_document(self, document, doc_type):
        if document_name in documents:
    
cache = CouchdbkitCache()
register_view = cache.register_view
register_func = cache.register_func
register_show = cache.register_show
register_list = cache.register_list               

class ViewDef(object):
    
    def __init__(self, name, fun_map=None, reduce_map=None, 
            language='javascript'):
            
        if not "/" in name:
            raise ValueError("%s is invalid. should be 'dname/vname" % name)
        
        self.name = name
        self.fun_map = fun_map
        self.reduce_map = reduce_map
        self.language = language
        
        register_view(name, self)
        
    def __call__(self, db, wrapper=None):
        return View(db, wrapper=wrappper)
        
    
        