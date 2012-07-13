//
//  STStampedActions.m
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampedActions.h"
#import "STSimpleAction.h"
#import "STSimpleSource.h"
#import "EntityDetailViewController.h"
#import "STStampDetailViewController.h"
#import "STStampedAPI.h"
#import "STMenuPopUp.h"
#import "STActionManager.h"
#import "STUserViewController.h"
#import "STPhotoViewController.h"
#import "STCreateStampViewController.h"
#import "CreateStampViewController.h"
#import "STImageCache.h"
#import "STConfirmationView.h"

@interface STStampedActions ()

- (BOOL)didChooseSource:(id<STSource>)source 
              forAction:(NSString*)action 
            withContext:(STActionContext*)context 
          shouldExecute:(BOOL)flag;
@end

@implementation STStampedActions

static STStampedActions* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STStampedActions alloc] init];
}

+ (STStampedActions*)sharedInstance {
    return _sharedInstance;
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    return [self didChooseSource:source forAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    [self didChooseSource:source forAction:action withContext:context shouldExecute:YES];
}


- (BOOL)didChooseSource:(id<STSource>)source 
              forAction:(NSString*)action 
            withContext:(STActionContext*)context 
          shouldExecute:(BOOL)flag {
    BOOL handled = NO;
    if ([source.source isEqualToString:@"stamped"]) {
        if ([action isEqualToString:@"stamped_view_entity"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                EntityDetailViewController* detailViewController = [[[EntityDetailViewController alloc] initWithEntityID:source.sourceID] autorelease] ;
                [[Util sharedNavigationController] pushViewController:detailViewController animated:YES];
            }
        }
        else if ([action isEqualToString:@"stamped_view_stamp"] && source.sourceID != nil) {
            UIViewController* controller = nil;
            if (context.stamp && [context.stamp.stampID isEqualToString:source.sourceID]) {
                handled = YES;
                if (flag) {
                    controller = [[[STStampDetailViewController alloc] initWithStamp:context.stamp] autorelease];
                }
            }
            else {
                handled = YES;
                if (flag) {
                    [STActionManager lock];
                    [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
                        BOOL unlocked = [STActionManager unlock];
                        if (unlocked) {
                            if (stamp) {
                                [[Util sharedNavigationController] pushViewController:[[[STStampDetailViewController alloc] initWithStamp:stamp] autorelease]
                                                                             animated:YES];
                            }
                            else {
                                [Util warnWithAPIError:error andBlock:nil];
                            }
                        }
                    }];
                }
            }
            if (controller) {
                [[Util sharedNavigationController] pushViewController:controller animated:YES];
            }
        }
        else if ([action isEqualToString:@"stamped_view_user"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                UIViewController* controller = nil;
                if (context.user) {
                    controller = [[[STUserViewController alloc] initWithUser:context.user] autorelease];
                }
                if (controller) {
                    [Util pushController:controller modal:NO animated:YES];
                }
                else {
                    [STActionManager lock];
                    [[STStampedAPI sharedInstance] userDetailForUserID:source.sourceID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
                        BOOL unlocked = [STActionManager unlock];
                        if (unlocked) {
                            if (userDetail) {
                                [Util pushController:[[[STUserViewController alloc] initWithUser:userDetail] autorelease] 
                                               modal:NO
                                            animated:YES];
                            }
                            else {
                                [Util warnWithMessage:@"User not found" andBlock:nil];
                            }
                        }
                    }];
                }
            }
        }
        else if ([action isEqualToString:@"stamped_view_screen_name"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                UIViewController* controller = nil;
                if (context.user) {
                    controller = [[[STUserViewController alloc] initWithUser:context.user] autorelease];
                }
                
                if (controller) {
                    [[Util sharedNavigationController] pushViewController:controller animated:YES];
                }
                else {
                    [STActionManager lock];
                    [[STStampedAPI sharedInstance] userDetailForScreenName:source.sourceID andCallback:^(id<STUserDetail> userDetail, NSError *error, STCancellation *cancellation) {
                        BOOL unlocked = [STActionManager unlock];
                        if (unlocked) {
                            if (userDetail) {
                                [[Util sharedNavigationController] pushViewController:[[[STUserViewController alloc] initWithUser:userDetail] autorelease] 
                                                                             animated:YES];
                            }
                            else {
                                [Util warnWithAPIError:error andBlock:nil];
                            }
                        }
                    }];
                }
            }
        }
        else if ([action isEqualToString:@"stamped_like_stamp"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                [[STStampedAPI sharedInstance] likeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
                    if (context.completionBlock) {
                        context.completionBlock(stamp, error);
                    }
                }];
            }
        }
        else if ([action isEqualToString:@"stamped_unlike_stamp"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                [[STStampedAPI sharedInstance] unlikeWithStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
                    if (context.completionBlock) {
                        context.completionBlock(stamp, error);
                    }
                }];
            }
        }
        else if ([action isEqualToString:@"stamped_todo_stamp"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
                    if (stamp) {
                        [[STStampedAPI sharedInstance] todoWithStampID:stamp.stampID entityID:stamp.entity.entityID andCallback:^(id<STTodo> todo, NSError* error2, STCancellation* can2) {
                            if (context.completionBlock) {
                                context.completionBlock(todo, error2);
                            }
                        }];
                    }
                    else {
                        if (context.completionBlock) {
                            context.completionBlock(nil, error);
                        }
                    }
                }];
            }
        }
        else if ([action isEqualToString:@"stamped_untodo_stamp"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                void (^block)(id<STStamp>, NSError*, STCancellation*) = ^(id<STStamp> stamp, NSError* error, STCancellation* cancellation) {
                    [[STStampedAPI sharedInstance] untodoWithStampID:stamp.stampID entityID:stamp.entity.entityID andCallback:^(BOOL success, NSError * error, STCancellation* can2) {
                        if (context.completionBlock) {
                            context.completionBlock([NSNumber numberWithBool:success], error);
                        }
                    }];
                };
                if (context.stamp) {
                    block(context.stamp, nil, [STCancellation cancellation]);
                }
                else {
                    [[STStampedAPI sharedInstance] stampForStampID:source.sourceID andCallback:block];
                }
            }
        }
        else if ([action isEqualToString:@"stamped_delete_stamp"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                [[STStampedAPI sharedInstance] deleteStampWithStampID:source.sourceID andCallback:^(BOOL success, NSError* error) {
                    if (context.completionBlock) {
                        context.completionBlock([NSNumber numberWithBool:success], error);
                    }
                }];
            }
        }
        else if ([action isEqualToString:@"stamped_view_image"] && source.sourceID != nil) {
            handled = YES;
            if (flag) {
                STPhotoViewController *controller = [[[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:source.sourceID]] autorelease];
                [[Util sharedNavigationController] pushViewController:controller animated:YES];
            }
        }
        else if ([action isEqualToString:@"stamped_view_user_image"] && context.user) {
            handled = YES;
            if (flag) {
                
                STPhotoViewController *controller = [[[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:context.user.imageURL]] autorelease];
                [[Util sharedNavigationController] pushViewController:controller animated:YES];
            }
        }
        else if ([action isEqualToString:@"stamped_confirm"] && source.sourceData != nil) {
            handled = YES;
            if (flag) {
                NSString* title = [source.sourceData objectForKey:@"title"];
                NSString* subtitle = [source.sourceData objectForKey:@"subtitle"];
                NSString* iconURL = [source.sourceData objectForKey:@"icon"];
                UIImage* icon = [[STImageCache sharedInstance] cachedImageForImageURL:iconURL];
                STConfirmationView* view = [[[STConfirmationView alloc] initWithTille:title subtitle:subtitle andIconImage:icon] autorelease];
                view.frame = [Util centeredAndBounded:view.frame.size inFrame:[Util fullscreenFrameAdjustedForStatusBar]];
                [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor colorWithWhite:0 alpha:.1]];
                if (!icon && iconURL) {
                    [[STImageCache sharedInstance] imageForImageURL:iconURL andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                        view.image = image; 
                    }];
                }
            }
        }
        else if ([action isEqualToString:@"stamped_view_create_stamp"] && source.sourceID != nil && context.entity) {
            handled = YES;
            if (flag) {
                CreateStampViewController* controller = [[[CreateStampViewController alloc] initWithEntity:context.entity] autorelease];
                controller.creditUsers = context.creditedUsers;
                [[Util sharedNavigationController] pushViewController:controller animated:YES];
            }
        }
        else if ([action isEqualToString:@"menu"] && source.sourceID != nil && context.entityDetail) {
            handled = YES;
            NSLog(@"menu handled");
            if (flag) {
                [Util globalLoadingLock];
                [[STStampedAPI sharedInstance] menuForEntityID:source.sourceID andCallback:^(id<STMenu> menu, NSError* error, STCancellation* cancellation) {
                    [Util globalLoadingUnlock];
                    NSAssert(context.entityDetail != nil, @"Context was modified after action was chosen"); 
                    if (menu) {
                        UIView* popUp = [[[STMenuPopUp alloc] initWithEntityDetail:context.entityDetail andMenu:menu] autorelease];
                        [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.75]];
                        if (context.completionBlock) {
                            context.completionBlock(menu, nil);
                        }
                    }
                    else {
                        [Util warnWithAPIError:error andBlock:^{
                            if (context.completionBlock) {
                                context.completionBlock(nil, error); 
                            }
                        }];
                    }
                }];
            }
        }
    }
    return handled;
}

- (void)viewStampWithStampID:(NSString*)stampID {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewStamp:stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)viewUserWithUserID:(NSString*)userID {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewUser:userID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}


+ (id<STAction>)actionViewEntity:(NSString*)entityID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_view_entity" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:entityID]];
}

+ (id<STAction>)actionViewStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_view_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionViewUser:(NSString*)userID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_view_user" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:userID]];
}

+ (id<STAction>)actionLikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_like_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionUnlikeStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_unlike_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionTodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_todo_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionUntodoStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_untodo_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionDeleteStamp:(NSString*)stampID withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_delete_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:stampID]];
}

+ (id<STAction>)actionViewImage:(NSString*)imageURL withOutputContext:(STActionContext*)context {
    return [STSimpleAction actionWithType:@"stamped_view_image" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:imageURL]];
}

+ (id<STAction>)actionViewUserImage:(id<STUser>)user withOutputContext:(STActionContext*)context {
    context.user = user;
    return [STSimpleAction actionWithType:@"stamped_view_user_image" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:user.userID]];
}

+ (id<STAction>)actionViewCreateStampWithEntity:(id<STEntity>)entity creditedUsers:(NSArray<STUser>*)users withOutputContext:(STActionContext*)context {
    context.creditedUsers = users;
    context.entity = entity;
    return [STSimpleAction actionWithType:@"stamped_view_create_stamp" 
                                andSource:[STSimpleSource sourceWithSource:@"stamped" andSourceID:entity.entityID]];
    
}

@end
