//
//  STStampsViewSource.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STGenericCollectionSlice.h"
#import "STStamp.h"
#import "STTypes.h"
#import "STCancellation.h"

@class STStampsViewSource;

@protocol STStampsViewSourceDelegate <NSObject>

- (void)shouldSetScopeTo:(STStampedAPIScope)scope;

@end

@interface STStampsViewSource : NSObject <UITableViewDataSource, UITableViewDelegate>

- (void)reloadStampedData;
- (STCancellation*)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice 
                                   andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block;
- (void)selectedNoStampsCell;
- (void)selectedLastCell;
- (void)cancelPendingOperations;
- (void)resumeOperations;
- (void)reduceStampCache;
- (id<STStamp>)stampForIndexPath:(NSIndexPath*)path;

@property (nonatomic, readwrite, assign) BOOL showSearchBar;
@property (nonatomic, readwrite, assign) NSInteger mainSection;
@property (nonatomic, readwrite, retain) STGenericCollectionSlice* slice;
@property (nonatomic, readwrite, retain) UITableView* table;
@property (nonatomic, readonly, retain) NSString* noStampsText;
@property (nonatomic, readonly, retain) NSString* lastCellText;
@property (nonatomic, readonly, retain) NSString* loadingText;
@property (nonatomic, readwrite, copy) NSSet* flareSet;
@property (nonatomic, readwrite, assign) id<STStampsViewSourceDelegate> delegate;

@end
