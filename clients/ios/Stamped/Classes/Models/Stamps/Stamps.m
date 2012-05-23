//
//  Stamps.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "Stamps.h"
#import "STConfiguration.h"
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"

#define kStampLimit 20

@implementation Stamps

@synthesize reloading=_reloading;
@synthesize moreData=_moreData;
@synthesize scope=_scope;
@synthesize searchQuery=_searchQuery;
@synthesize identifier;

- (id)init {
  if ((self = [super init])) {
    
      _data = [[NSArray alloc] init];
      _identifiers = [[NSArray alloc] init];
      _moreData = NO;

      
  }
  return self;
}

- (void)dealloc {
    [self cancel];
    [_identifiers release], _identifiers=nil;
    [_data release], _data=nil;
    [super dealloc];
}


#pragma mark - Stamps Loading

/*
 # Paging
 cls.addProperty('before',               int)
 cls.addProperty('limit',                int)
 cls.addProperty('offset',               int)
 
 # Filtering
 cls.addProperty('category',             basestring)
 cls.addProperty('subcategory',          basestring)
 cls.addProperty('viewport',             basestring) # lat0,lng0,lat1,lng1
 
 # Scope
 cls.addProperty('user_id',              basestring)
 cls.addProperty('scope',                basestring) # me, inbox, friends, fof, popular
 */

/*
 * /v0/stamps/search.json
 */

- (NSString*)scopeString {
    
    switch (_scope) {
        case STStampedAPIScopeYou:
            return @"me";
            break;
        case STStampedAPIScopeFriends:
            return @"friends";
            break;
        case STStampedAPIScopeFriendsOfFriends:
            return @"fof";
            break;
        case STStampedAPIScopeEveryone:
            return @"popular";
            break;
        default:
            break;
    }
    
    return @"me";
    
}

- (void)loadWithPath:(NSString*)path params:(NSDictionary*)params {
        
    _cancellation = [[[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleStamp mapping] andCallback:^(NSArray* stamps, NSError* error, STCancellation* cancellation) {

        _moreData = NO;
        if (stamps) {
            
            NSLog(@"count : %i", [stamps count]);
            _moreData = ([stamps count] == kStampLimit);
            
            NSMutableArray *array = [_data mutableCopy];
            NSMutableArray *identifiers = [_identifiers mutableCopy];

            for (id<STStamp> stamp in stamps) {
                                                
                if (![identifiers containsObject:stamp.stampID]) {
                    
                    if (![stamp.deleted boolValue]) {
                        [array addObject:stamp];
                        [identifiers addObject:stamp.stampID];
                    }
                    
                    
                } else {
                    
                    if ([stamp.deleted boolValue]) {
                        
                        if ([_identifiers containsObject:stamp.stampID]) {
                            
                            NSInteger index = [identifiers indexOfObject:stamp.stampID];
                            if (index!=NSNotFound) {
                                [identifiers removeObjectAtIndex:index];
                                [array removeObjectAtIndex:index];
                            }
                            
                        }
                    }
                }
            }
            
            [_data release], _data = nil;
            [_identifiers release], _identifiers = nil;
            
            _data = [array retain];
            _identifiers = [identifiers retain];
            [_cancellation release], _cancellation=nil;
            
            [array release];
            [identifiers release];
            
        }
                
        _reloading = NO;
        dispatch_async(dispatch_get_main_queue(), ^{
            [[NSNotificationCenter defaultCenter] postNotificationName:[NSString stringWithFormat:@"stamps-%@", self.identifier] object:nil];
        });
        
    }] retain];
    
}

- (void)searchWithQuery:(NSString*)query {
    
    [self cancel];
    NSString *limit = [NSString stringWithFormat:@"%i", kStampLimit];
    [self loadWithPath:@"stamps/search.json" params:[NSDictionary dictionaryWithObjectsAndKeys:query, @"query", limit, @"limit", nil]];

}

- (void)reloadData {
    if (_reloading) return;
    _reloading = YES;
    
    if ([_data count] > 0) {
        
        // add before
        
    }

    NSString *limit = [NSString stringWithFormat:@"%i", kStampLimit];
    [self loadWithPath:@"stamps/collection.json" params:[NSDictionary dictionaryWithObjectsAndKeys:[self scopeString], @"scope", limit, @"limit", nil]];
  
}

- (void)loadNextPage {
    if (_reloading) return;
    _reloading = YES;

    _page++;
    NSString *offset = [NSString stringWithFormat:@"%i", _page];
    NSString *limit = [NSString stringWithFormat:@"%i", kStampLimit];
    [self loadWithPath:@"stamps/collection.json" params:[NSDictionary dictionaryWithObjectsAndKeys:[self scopeString], @"scope", limit, @"limit", offset, @"offset", nil]];
    
}

- (void)cancel {
  
    if (_cancellation) {
        [_cancellation cancel];
    }
    _reloading = NO;
    
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    
    if (_scope != scope) {
        _scope = scope;
        [self cancel];
        _data = [[NSArray alloc] init];
        _identifiers = [[NSArray alloc] init];
    }
    
}


#pragma mark - Stamps Data Source

- (id)stampAtIndex:(NSInteger)index {
    return [_data objectAtIndex:index];
}

- (NSInteger)numberOfStamps {
    return [_data count];
}

- (BOOL)isEmpty {
    return ([_data count] == 0);
}





@end