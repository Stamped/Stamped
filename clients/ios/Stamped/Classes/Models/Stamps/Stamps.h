//
//  Stamps.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <Foundation/Foundation.h>
#import "STStampedAPI.h"

@interface Stamps : NSObject

@property (nonatomic, copy) NSString *identifier;
@property (nonatomic, readonly, getter = isReloading) BOOL reloading;
@property (nonatomic, readonly, getter = hasMoreData) BOOL moreData;
@property (nonatomic, assign) STStampedAPIScope scope;
@property (nonatomic, copy) NSString *searchQuery;

/*
 * Stamps loading
 */
- (void)reloadData;
- (void)loadNextPage;
- (void)cancel;

/*
 * Stamps data source
 */
- (id)stampAtIndex:(NSInteger)index;
- (NSInteger)numberOfStamps;
- (BOOL)isEmpty;

/*
 * Searching
 */
- (void)searchWithQuery:(NSString*)query;

@end