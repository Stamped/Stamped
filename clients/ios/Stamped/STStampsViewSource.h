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

@interface STStampsViewSource : NSObject <UITableViewDataSource, UITableViewDelegate>

- (void)reloadStampedData;
- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block;
- (void)selectedNoStampsCell;
- (void)selectedLastCell;

@property (nonatomic, readwrite, retain) STGenericCollectionSlice* slice;
@property (nonatomic, readwrite, retain) UITableView* table;
@property (nonatomic, readwrite, retain) NSString* noStampsText;
@property (nonatomic, readwrite, retain) NSString* lastCellText;
@property (nonatomic, readwrite, retain) NSString* loadingText;

@end
