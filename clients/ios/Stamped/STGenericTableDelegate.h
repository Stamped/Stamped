//
//  STGenericTableDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STTableDelegate.h"
#import "STLazyList.h"
#import "STTableViewCellFactory.h"

@protocol STGenericTableDelegateDelegate;

@interface STGenericTableDelegate : NSObject <STTableDelegate>

@property (nonatomic, readwrite, retain) id<STLazyList> lazyList;
@property (nonatomic, readwrite, retain) id<STTableViewCellFactory> tableViewCellFactory;
@property (nonatomic, readwrite, copy) void (^selectedCallback)(STGenericTableDelegate* tableDelegate, UITableView* tableView, NSIndexPath* path);
@property (nonatomic, readwrite, copy) UITableViewCell* (^noDataFactory)(STGenericTableDelegate* tableDelegate, UITableView* tableView);
@property (nonatomic, readwrite, copy) NSString* style;
@property (nonatomic, readwrite, assign) NSInteger pageSize;
@property (nonatomic, readwrite, assign) NSInteger preloadBufferSize;
@property (nonatomic, readwrite, assign) BOOL loadingCellDisabled;
@property (nonatomic, readwrite, assign) BOOL autoPrepareDisabled;

@property (nonatomic, readwrite, assign) id<STGenericTableDelegateDelegate> delegate;

- (void)cancelPendingRequests;

@end

@protocol STGenericTableDelegateDelegate <NSObject>

- (void)tableDelegate:(STGenericTableDelegate*)tableDelegate didFinishLoadingWithCount:(NSInteger)count;

@end
