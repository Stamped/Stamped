//
//  STUserStamps.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <Foundation/Foundation.h>

@interface STUserStamps : NSObject


@property(nonatomic,readonly,getter = isReloading) BOOL reloading;
@property(nonatomic,readonly,getter = hasMore) BOOL moreData;
@property(nonatomic,copy) NSString *userIdentifier;

- (void)reloadData;
- (void)loadNextPage;

- (id)objectAtIndex:(NSInteger)index;
- (NSInteger)numberOfObject;
- (BOOL)isEmpty;

@end
