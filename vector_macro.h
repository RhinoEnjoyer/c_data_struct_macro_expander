//#include <stdint.h>
//#include <memory.h>
//#include <malloc.h>

#define vALLOC(T,v,s)       vec_##T##_alloc(v,s)
#define vREALLOC(T,v,s)     vec_##T##_realloc(v,s)
#define vDEALLOC(T,v)       vec_##T##_dealloc(v)
#define vINIT(T,v,s)        vec_##T##_init(v,s)
#define vCOPY(T,this,other) vec_##T##_copy(this,other)
#define vPUSH(T,v,va)       vec_##T##_push(v,va)

//#define VECTOR_FUNCTION_PREFIX __attribute__((always_inline)) inline

//#define vec(T) vec_##T
//#define vec_dealloc_attrib(T) __attribute__((cleanup(vec_##T##_dealloc)))


#define VECTOR_DEFINE(T)\
typedef struct _vec_##T{\
 T* ptr;\
 uint64_t count;\
 uint64_t capacity;\
} vec_##T;\
\
\
VECTOR_FUNCTION_PREFIX static T* const vec_##T##_elm(vec_##T* v,uint64_t i){\
  return &v->ptr[i];\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_alloc(vec_##T* v ,uint64_t s){\
  if(s == 0) v->ptr = NULL;\
  else v->ptr = (T*)calloc(s,sizeof(T));\
  v->capacity = s;\
  v->count = 0;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_dealloc(vec_##T* v){\
  if(v->ptr){\
    free(v->ptr);\
    v->ptr = NULL;\
    v->count = 0;\
    v->capacity = 0;\
  }\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_realloc(vec_##T* v , uint64_t s){\
  if( v->ptr && v->capacity != s && v->capacity != 0) v->ptr = (T*)realloc(v->ptr,s*sizeof(T));\
  else vALLOC(T,v,s);\
  v->capacity = s;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_expand(vec_##T* v , uint64_t s){\
  if( v->ptr && v->capacity != 0 && s != 0) v->ptr = (T*)realloc(v->ptr,(s + v->capacity)*sizeof(T));\
  else vALLOC(T,v,s + v->capacity);\
  v->capacity += s;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_copy(vec_##T* t,vec_##T* o){\
   t->count     = o->count;\
   t->capacity  = o->capacity;\
   vREALLOC(T ,t ,o->count);\
   memcpy(t->ptr ,o->ptr ,sizeof(T)*o->count);\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_move(vec_##T* dst,vec_##T* o){\
   dst->count     = o->count;\
   dst->capacity  = o->capacity;\
   vREALLOC(T ,dst ,o->count);\
   dst->ptr = o->ptr;\
   o->ptr = NULL;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_init(vec_##T* v ,uint64_t s){\
    vALLOC(T,v,s);\
    v->count = 0;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_empty(vec_##T* v){\
    v->ptr = NULL;\
    v->count = 0;\
    v->capacity = 0;\
}\
\
VECTOR_FUNCTION_PREFIX static void vec_##T##_push(vec_##T* v,T value){\
    if(v->count == v->capacity) {vREALLOC(T,v,v->capacity*2);}\
    \
    v->ptr[v->count] = value;\
    v->count++;\
}\
VECTOR_FUNCTION_PREFIX static T vec_##T##_pop(vec_##T* v,uint64_t index){\
    T r = *vec_##T##_elm(v,index);\
    memcpy(v->ptr + index, v->ptr + index + 1, ((v->count-1)-index)*sizeof(T));\
    v->count-=1;\
    return r;\
}\

