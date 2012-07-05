//
//  STUserStamps.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserStamps.h"
#import "STConfiguration.h"
#import "STRestKitLoader.h"
#import "STSimpleStamp.h"
#import "STDebug.h"
#import "Util.h"
#import "STEvents.h"

#define kStampLimit 20

@interface STUserStamps ()
@property (nonatomic, readwrite, retain) NSArray* data;
@property (nonatomic, readwrite, retain) NSArray* identifiers;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readwrite, assign) NSInteger page;
@end

@implementation STUserStamps

@synthesize reloading=_reloading;
@synthesize moreData=_moreData;
@synthesize data = _data;
@synthesize identifiers = _identifiers;
@synthesize cancellation = _cancellation;
@synthesize page = _page;
@synthesize userIdentifier;

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

- (void)loadWithPath:(NSString*)path params:(NSDictionary*)params {
    
    /*
     _cancellation = [[[STStampedAPI sharedInstance] stampsWithUserID:self.userIdentifier date:[NSDate date] limit:kStampLimit offset:_page andCallback:^(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation) {
     */
    
    _cancellation = [[[STRestKitLoader sharedInstance] loadWithPath:path post:NO authenticated:YES params:params mapping:[STSimpleStamp mapping] andCallback:^(NSArray* stamps, NSError* error, STCancellation* cancellation) {
        
        _moreData = NO;
        if (stamps) {
            
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
        [STEvents postEvent:EventTypeUserStampsFinished identifier:self.userIdentifier object:nil];
        
    }] retain];
    
}

- (void)reloadData {
    if (_reloading) return;
    _reloading = YES;
    
    [self loadWithPath:@"/stamps/collection.json" params:[NSDictionary dictionaryWithObjectsAndKeys:self.userIdentifier, @"user_id", [NSNumber numberWithInt:kStampLimit], @"limit", [NSNumber numberWithInteger:[[NSDate date] timeIntervalSince1970]], @"before", @"user", @"scope", nil]];
    
}

- (void)loadNextPage {
    if (_reloading) return;
    _reloading = YES;
    
    _page++;
    [self loadWithPath:@"/stamps/collection.json" params:[NSDictionary dictionaryWithObjectsAndKeys:self.userIdentifier, @"user_id", [NSNumber numberWithInt:kStampLimit], @"limit", [NSNumber numberWithInteger:[[NSDate date] timeIntervalSince1970]], @"before", @"user", @"scope", [NSNumber numberWithInt:_page], @"offset", nil]];
    
}

- (void)cancel {
    
    if (_cancellation) {
        [_cancellation cancel];
    }
    _reloading = NO;
    
}


#pragma mark - Stamps Data Source

- (id)objectAtIndex:(NSInteger)index {
    return [_data objectAtIndex:index];
}

- (NSInteger)numberOfObject {
    return [_data count];
}

- (BOOL)isEmpty {
    return ([_data count] == 0);
}





@end