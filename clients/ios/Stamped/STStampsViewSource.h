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
#import "STScopeSlider.h"

@class STStampsViewSource;

@protocol STStampsViewSourceDelegate <NSObject>

- (void)shouldSetScopeTo:(STStampedAPIScope)scope;

@end

@interface STStampsViewSource : NSObject <UITableViewDataSource, UITableViewDelegate>

- (void)reloadStampedData;
- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block;
- (void)selectedNoStampsCell;
- (void)selectedLastCell;

@property (nonatomic, readwrite, assign) NSInteger mainSection;
@property (nonatomic, readwrite, retain) STGenericCollectionSlice* slice;
@property (nonatomic, readwrite, retain) UITableView* table;
@property (nonatomic, readonly, retain) NSString* noStampsText;
@property (nonatomic, readonly, retain) NSString* lastCellText;
@property (nonatomic, readonly, retain) NSString* loadingText;
@property (nonatomic, readwrite, copy) NSSet* flareSet;
@property (nonatomic, readwrite, assign) id<STStampsViewSourceDelegate> delegate;

@end
