//
//  Stamps.h
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import <Foundation/Foundation.h>
#import "STStampedAPI.h"

extern NSString* const StampsChangedNotification;

@interface Stamps : NSObject

@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString *searchQuery;

/*
 * Stamps loading
 */
- (void)reloadData;
- (void)loadNextPage;
- (void)cancel;

/*
 * Stamps data source
 */
- (NSString*)stampIDAtIndex:(NSInteger)index;
- (NSInteger)numberOfStamps;
- (BOOL)isEmpty;
- (BOOL)hasMoreData;
- (BOOL)isReloading;

+ (Stamps*)sharedInstance;

@end
