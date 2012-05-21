//
//  Stamps.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "Stamps.h"
#import "STConfiguration.h"

@implementation Stamps

@synthesize reloading=_reloading;
@synthesize moreData=_moreData;
@synthesize scope=_scope;
@synthesize searchQuery=_searchQuery;

- (id)init {
    if ((self = [super init])) {
        
        _data = [[NSArray alloc] init];
        _moreData = NO;
        
        STGenericCollectionSlice *slice = [[STGenericCollectionSlice alloc] init];
        slice.sort = [STConfiguration value:@"Root.inboxSort"];
        _slice = [slice retain];
        [slice release];
        
    }
    return self;
}

- (void)dealloc {
    [self cancel];
    [_data release], _data=nil;
    [_slice release], _slice=nil;
    [super dealloc];
}


#pragma mark - Stamps Loading

- (void)loadWithPath:(NSString*)path {


    
    

    
}

- (void)reloadData {
    if (_reloading) return;
    _reloading = YES;
    
    NSLog(@"RELOADING");
    
    [[STStampedAPI sharedInstance] stampsForInboxSlice:_slice andCallback:^(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation){
        
        NSLog(@"finished : %@", [stamps description]);
        _reloading = NO;
        
    }];
    
}

- (void)loadNextPage {
    
    
    
    
}

- (void)cancel {
    
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    _scope = scope;
    
    STGenericCollectionSlice *slice = nil;
    
    switch (scope) {
        case STStampedAPIScopeYou: {
            STUserCollectionSlice *tempSlice = [[STUserCollectionSlice alloc] init];
            tempSlice.userID = [[STStampedAPI sharedInstance].currentUser userID];
            slice = tempSlice;
        }
            break;
        case STStampedAPIScopeFriends: {
            STGenericCollectionSlice* tempSlice = [[STGenericCollectionSlice alloc] init];
            slice = tempSlice;
        }
            break;
        case STStampedAPIScopeFriendsOfFriends: {
            STFriendsSlice *tempSlice = [[STFriendsSlice alloc] init];
            tempSlice.distance = [NSNumber numberWithInteger:2];
            tempSlice.inclusive = [NSNumber numberWithBool:NO];
            slice = tempSlice;
        }
            break;            
        default: {
            STGenericCollectionSlice* tempSlice = [[STGenericCollectionSlice alloc] init];
            slice = tempSlice;
        }
            break;
    }
    
    slice.query = _searchQuery;
    slice.sort = @"relevance";
    
    [_slice release], _slice = nil;
    _slice = (id)[slice retain];
    [slice release];
    
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
