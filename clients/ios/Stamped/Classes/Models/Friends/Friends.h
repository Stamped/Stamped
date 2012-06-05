//
//  Friends.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <Foundation/Foundation.h>

typedef enum {
    FriendsRequestTypeContacts = 0,
    FriendsRequestTypeFacebook,
    FriendsRequestTypeTwitter,
    FriendsRequestTypeSuggested,
} FriendsRequestType;

@interface Friends : NSObject {
    NSArray *_data;
    NSArray *_identifiers;
    STCancellation *_cancellation;
}

@property(nonatomic,assign) FriendsRequestType requestType;
@property(nonatomic,readonly,getter = isReloading) BOOL reloading;
@property(nonatomic,readonly,getter = hasMore) BOOL moreData;
@property(nonatomic,retain) NSDictionary *requestParameters;


- (void)reloadData;
- (void)loadNextPage;


/*
 * DataSource
 */

- (NSInteger)numberOfObjects;
- (id)objectAtIndex:(NSInteger)index;
- (BOOL)isEmpty;
@end
